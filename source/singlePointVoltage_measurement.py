"""Perform a single point measurement. Implemented with the DMM driver."""

import logging
import math
import pathlib
from enum import Enum
from typing import Tuple

import click
import ni_measurementlink_service as nims
import nidmm
from _helpers import (
    ServiceOptions,
    configure_logging,
    create_session_management_client,
    get_grpc_device_channel,
    get_service_options,
    grpc_device_options,
    use_simulation_option,
    verbosity_option,
)
from _nidmm_helpers import create_session

service_directory = pathlib.Path(__file__).resolve().parent
measurement_service = nims.MeasurementService(
    service_config_path=service_directory / "singlePointVoltage.serviceconfig",
    version="1.0.0.0",
    ui_file_paths=[service_directory / "singlePointVoltage.measui"],
)
service_options = ServiceOptions()

RESERVATION_TIMEOUT_IN_SECONDS = 60.0
"""
If another measurement is using the session, the reserve function will wait
for it to complete. Specify a reservation timeout to aid in debugging missed
unreserve calls. Long measurements may require a longer timeout.
"""


class VoltageFunction(Enum):
    """DMM Voltage wrapper enum that contains a zero value."""

    DC = 0
    AC = 1
    AC_VOLTS_DC_COUPLED = 2

    def convert_to_dmm_value(self):
        """Converts the enum value to the DMM apporpriate value.

        Enum requires whole numbers and GRPC setup needs 0.
        """
        if self.name == "AC":
            return nidmm.Function.AC_VOLTS.value
        if self.name == "AC_VOLTS_DC_COUPLED":
            return nidmm.Function.AC_VOLTS_DC_COUPLED.value
        return nidmm.Function.DC_VOLTS.value


class ResolutionDigits(Enum):
    """DMM Digits of Resolution wrapper enum that contains a zero value.."""

    DIGITS_3_5 = 0
    DIGITS_4_5 = 1
    DIGITS_5_5 = 2
    DIGITS_6_5 = 3
    DIGITS_7_5 = 4

    def convert_to_dmm_value(self):
        """Converts enum value to DMM appropriate value.

        Enum requires whole numbers and GRPC setup needs 0.
        """
        return self.value + 3.5


@measurement_service.register_measurement
@measurement_service.configuration(
    "channel_or_pin",
    nims.DataType.Pin,
    "Select a pin",
    instrument_type=nims.session_management.INSTRUMENT_TYPE_NI_DMM,
)
@measurement_service.configuration(
    "signal_type",
    nims.DataType.Enum,
    VoltageFunction.DC,
    enum_type=VoltageFunction,
)
@measurement_service.configuration("voltage_range", nims.DataType.Double, 5.0)
@measurement_service.configuration(
    "resolution_digits",
    nims.DataType.Enum,
    ResolutionDigits.DIGITS_5_5,
    enum_type=ResolutionDigits,
)
@measurement_service.output("measured_value", nims.DataType.Double)
@measurement_service.output("signal_out_of_range", nims.DataType.Boolean)
def measure(
    channel_or_pin: str,
    signal_type: VoltageFunction,
    voltage_range: float,
    resolution_digits: ResolutionDigits,
) -> Tuple:
    """Perform a measurement using an NI DMM."""
    logging.info(
        "Starting measurement: channel_or_pin_name=%s signal_type=%s range=%g resolution_digits=%g",
        channel_or_pin,
        signal_type.name,
        voltage_range,
        resolution_digits.convert_to_dmm_value(),
    )

    session_management_client = create_session_management_client(measurement_service)

    with session_management_client.reserve_session(
        context=measurement_service.context.pin_map_context,
        pin_or_relay_names=[channel_or_pin],
        instrument_type_id=nims.session_management.INSTRUMENT_TYPE_NI_DMM,
        timeout=RESERVATION_TIMEOUT_IN_SECONDS,
    ) as reservation:
        grpc_device_channel = get_grpc_device_channel(measurement_service, nidmm, service_options)
        with create_session(reservation.session_info, grpc_device_channel) as session:
            session.configure_measurement_digits(
                nidmm.Function(signal_type.convert_to_dmm_value()),
                voltage_range,
                resolution_digits.convert_to_dmm_value(),
            )
            measured_value = session.read(maximum_time=1000)
            signal_out_of_range = math.isnan(measured_value) or math.isinf(measured_value)

    logging.info(
        "Completed measurement: measured_value=%g signal_out_of_range=%s",
        measured_value,
        signal_out_of_range,
    )
    return (measured_value, signal_out_of_range)


@click.command
@verbosity_option
@grpc_device_options
@use_simulation_option(default=False)
def main(verbosity: int, **kwargs) -> None:
    """Perform a measurement using an NI DMM."""
    configure_logging(verbosity)
    global service_options
    service_options = get_service_options(**kwargs)
    with measurement_service.host_service():
        input("Press enter to close the measurement service.\n")


if __name__ == "__main__":
    main()
