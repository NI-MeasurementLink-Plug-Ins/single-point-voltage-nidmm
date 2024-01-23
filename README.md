# Getting Started
Follow the instructions on the [MeasurementLink-Python GitHub page](https://github.com/ni/measurementlink-python#developing-measurements-quick-start) for building and running this measurement.

# Additional notes about this measurement:
- This measurement supports `nidmm` and depends on `ni-measurementlink-service 1.2.0`.
- The overall measurement structure was heavily based on the [DMM example for MeasurementLink Support for Python v1.2.0](https://github.com/ni/measurementlink-python/releases/tag/1.2.0). 
  - The **_helpers.py** and **_nidmm_helpers.py** were copied directly from the MeasurementLink Team's example. 
  - Use the example's **teststand_fixture.py** to to manage the hardware resource in TestStand.
- The recommended hardware for this measurement is PXIe-4081.