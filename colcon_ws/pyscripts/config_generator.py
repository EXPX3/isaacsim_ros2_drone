import json

def generate_lidar_config(file_path):
    elevation_start = 0.0
    elevation_end = -45.0
    vertical_resolution = 1.0

    elevation_angles = [
        elevation_start + i * vertical_resolution
        for i in range(int((elevation_end - elevation_start) / vertical_resolution) + 1)
    ]

    emitters = {
        "azimuthDeg": [0] * len(elevation_angles),
        "elevationDeg": elevation_angles,
        "fireTimeNs": [0] * len(elevation_angles)
    }

    config = {
        "class": "sensor",
        "type": "lidar",
        "name": "lidar_vfov45_hfvov360_300kps",
        "driveWorksId": "GENERIC",
        "profile": {
            "scanType": "rotary",
            "intensityProcessing": "normalization",
            "rayType": "IDEALIZED",
            "nearRangeM": 0.05,
            "farRangeM": 100.0,
            "startAzimuthDeg": -180.0,
            "endAzimuthDeg": 180.0,
            "upElevationDeg": 0.0,
            "downElevationDeg": 45.0,
            "rangeResolutionM": 0.001,
            "rangeAccuracyM": 0.04,
            "avgPowerW": 3.6,
            "minReflectance": 0.1,
            "minReflectanceRange": 120.0,
            "wavelengthNm": 905.0,
            "pulseTimeNs": 23,
            "azimuthErrorMean": 0.0,
            "azimuthErrorStd": 0.0,
            "elevationErrorMean": 0.0,
            "elevationErrorStd": 0.0,
            "reportTypes": "Strongest",
            "maxReturns": 1,
            "scanRatesHz": [30.0],
            "scanRateBaseHz": 30.0,
            "reportRateBaseHz": 302400,
            "numberOfEmitters": len(elevation_angles),
            "emitters": emitters,
            "intensityMappingType": "LINEAR"
        }
    }

    with open(file_path, "w") as f:
        json.dump(config, f, indent=2)

# Save to this path (adjust if needed)
generate_lidar_config("/root/colcon_ws/rotating_vlp16/lidar_vfov45_hfvov360_fixed_.json")
