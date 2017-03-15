import cx_Oracle, csv, datetime, os, sys, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import Encoders
def sendMail(sender, recipient, files):
	COMMASPACE = ', '
	msg = MIMEMultipart()
	msg['Subject'] = 'IRIS Parcel Updates'
	msg['To'] = recipient
	msg['From'] = sender
	msg.preamble = 'Attached are the log files for the latest parcel update'
	for file in files:
		#with open(file, 'rb') as fp:
		#	csv = MIMEText(fp.read())
		#msg.attach(csv)
		part = MIMEBase('text/plain', 'octet-stream')
		part.set_payload(open(file, 'rb').read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
		msg.attach(part)
	s = smtplib.SMTP('cormailgw.raleighnc.gov')
	s.sendmail(sender, recipient, msg.as_string())
	print "mail sent"
	s.close()
	#s.send_message(msg)
	#s.quit()	
conn = cx_Oracle.connect(os.environ['IRISPRD_LOGIN'])
cursor = conn.cursor()
ucursor = conn.cursor()
cnt = 0
with open(os.path.dirname(sys.argv[0]) + 'parcels.csv', 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='|')
	updateMessages = [("PIN", "FIELD", "OLD VALUE", "NEW VALUE")]
	errorMessages = [("PIN", "ERROR")]
	for parcel in reader:
		cnt += 1
		print cnt
		statement = "SELECT NCPIN,PARC_IN_OUT_CITY_LIMITS,PARC_COUNCIL_DISTRICT,PARC_CAC,PARC_COMPREHNSVE_PLAN_DIST,PARC_INSPECTION_AREA_ID,PARC_THROUGHFARE_ZONE_FEE,PARC_OPEN_SPACE_ZONE_FEE,PARC_CENSUS_BLOCK_2010,PARC_CENSUS_TRACT_2010, UPDATE_APPLICATION_ID, UPDATE_USER_ID, UPDATE_DATE FROM iris.parcels WHERE ncpin = '" + parcel[0] + "' AND PARC_ACT_INACT_STATUS = 'A'"
		cursor.execute(statement)
		items = cursor.fetchmany()
		if len(items) == 0:
			errorMessages.append(('="' + parcel[0] + '"', "Not found in IRIS"))
			print "PIN " + parcel[0] + " not found in IRIS"
		for item in items:
			update = False
			updateCouncil = False
			updates = []
			updateStatement = "UPDATE IRIS.PARCELS SET "
			if str(item[1]) != str(parcel[1]):
				updates.append("PARC_IN_OUT_CITY_LIMITS = |" + str(parcel[1]) + "|")
				updateMessages.append(('="' + parcel[0] + '"' , "PARC_IN_OUT_CITY_LIMITS", str('' if item[1] is None else item[1]),str('' if parcel[1] is None else parcel[1])))
				update = True
			if str(item[2]) != str(parcel[2]):
				updates.append("PARC_COUNCIL_DISTRICT = |" + str(parcel[2]) + "|")
                                updateMessages.append(('="' + parcel[0] + '"',"PARC_COUNCIL_DISTRICT",str('' if item[2] is None else item[2]),str('' if parcel[2] is None else parcel[2])))				
				update = True
				updateCouncil = True
			if str(item[3]) != str(parcel[3]):
				updates.append("PARC_CAC = |" + str(parcel[3]) + "|")
                                updateMessages.append(('="' + parcel[0] + '"',"PARC_CAC", str('' if item[3] is None else item[3]),str('' if parcel[3] is None else parcel[3])))			
				update = True
			if str(item[4]) != str(parcel[4]):
				updates.append("PARC_COMPREHNSVE_PLAN_DIST = |" + str(parcel[4]) + "|")
                                updateMessages.append(('="' + parcel[0] + '"',"PARC_COMPREHNSVE_PLAN_DIST",str('' if item[4] is None else item[4]), str('' if parcel[4] is None else parcel[4])))
				update = True
			if str(item[5]) != str(parcel[5]):
				update = True
                                updateMessages.append(('="' + parcel[0] + '"', "PARC_INSPECTION_AREA_ID", str('' if item[5] is None else item[5]), str('' if parcel[5] is None else parcel[5])))
				if parcel[5] != "":
					updates.append("PARC_INSPECTION_AREA_ID = " + str(parcel[5]))
				else:
					updates.append("PARC_INSPECTION_AREA_ID = NULL")
			if str(item[6]) != str(parcel[6]):
				update = True
                                updateMessages.append(('="' + parcel[0] + '"', "PARC_THROUGHFARE_ZONE_FEE", str('' if item[6] is None else item[6]), str('' if parcel[6] is None else parcel[6])))
				print parcel
				print item
                                if parcel[5] != "":
                                        updates.append("PARC_THROUGHFARE_ZONE_FEE = " + str(parcel[6]))
                                else:
                                        updates.append("PARC_THROUGHFARE_ZONE_FEE = NULL")
			if str(item[7]) != str(parcel[7]):
				update = True
                                updateMessages.append(('="' + parcel[0] + '"', "PARC_OPEN_SPACE_ZONE_FEE", str('' if item[7] is None else item[7]),str('' if parcel[7] is None else parcel[7])))
                                if parcel[5] != "":
                                        updates.append("PARC_OPEN_SPACE_ZONE_FEE = " + str(parcel[7]))
                                else:
                                        updates.append("PARC_OPEN_SPACE_ZONE_FEE = NULL")

                        if str(item[8]) != str(parcel[8]):
                                update = True
                                updateMessages.append(('="' + parcel[0] + '"', "PARC_CENSUS_BLOCK_2010", str('' if item[8] is None else item[8]), str('' if parcel[8] is None else parcel[8])))
				updates.append("PARC_CENSUS_BLOCK_2010 = |" + str(parcel[8]) + "|")
                        if str(item[9]) != str(parcel[9]):
                                update = True
                                updateMessages.append(('="' + parcel[0] + '"', "PARC_CENSUS_TRACT_2010", str('' if item[9] is None else item[9]), str('' if parcel[9] is None else parcel[9])))
				updates.append("PARC_CENSUS_TRACT_2010 = |" + str(parcel[9]) + "|")
              		if update:
				updateStatement += str(updates).replace('[', '').replace(']','').replace("'", '').replace("|", "'")
				today = datetime.datetime.today().strftime('%m-%d-%Y')
				updateStatement += ", UPDATE_APPLICATION_ID = 'GIS SCAN', UPDATE_USER_ID = 'grecoj', UPDATE_DATE = TO_DATE('" + today + "', 'MM-DD-YYYY')" 
				updateStatement += " WHERE ncpin = '" + parcel[0] + "' AND PARC_ACT_INACT_STATUS = 'A'"
		
				print updateStatement
				ucursor.execute(updateStatement)
				if updateCouncil:
					updateStatement = "UPDATE IRIS.PARCELS SET PARC_PITOMETER_ZONE = TO_NUMBER(TO_CHAR(SYSDATE, 'MMYYYY')) WHERE NCPIN = '" + parcel[0] + "' AND PARC_ACT_INACT_STATUS = 'A'"
					ucursor.execute(updateStatement) 
conn.commit()
conn.close()
with open(os.path.dirname(sys.argv[0]) + 'updates.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile, delimiter=',')
	for message in updateMessages:
		writer.writerow(message)
with open(os.path.dirname(sys.argv[0]) + 'errors.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for message in errorMessages:
                writer.writerow(message)
sendMail('gis@raleighnc.gov', ['raleighaddressing@raleighnc.gov', 'gis@raleighnc.gov'], [os.path.dirname(sys.argv[0]) + 'updates.csv', os.path.dirname(sys.argv[0]) + 'errors.csv'])
