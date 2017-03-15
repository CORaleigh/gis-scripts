## Update IRIS Parcel Data

Python scripts to update parcel data in IRIS database using GIS data.  Data updated include the following:
* City Council District
* Citizen Advisory Council
* Thoroughfare Fee Zone
* Open Space Fee Zone
* Census Tract Number
* Census Block Number
* Comprehensive Plan Zone
* Inspector Area
Scripts are split into two scripts:
* updateirisdata.py
  * generated from ArcGIS model, spatial joins the above layers with the property layer and spits out a CSV file with PIN and the corresponding value for each layer.
* updateiris.py
  * loops through generated CSV file and updates any parcel with a differing value
  * used cx_Oracle module to connect to and update the IRIS database
