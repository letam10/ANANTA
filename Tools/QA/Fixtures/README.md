# City save compatibility fixture

CityBeforeServices.sav is an isolated QA save produced by the pre-services city build.
It was copied from Saved/QA/CityLegacySave/ANANTA_City_QA.sav on 2026-10-08.
It contains a completed mission and player/vehicle transforms, with no Services property.
It contains no normal player slot data.

- Bytes: 3183
- SHA256: 25fad839c72a77e946a498c5dd8892e9db45e99e0e85d897aaf60dbbe45e59c7
- Automation: ANANTA.City.Save.PreServicesFileCompatibility

Keep these original bytes. Generating this fixture with the new class would not test compatibility.
The test reads the file and performs its upgraded serialization entirely in memory.
