#!/usr/bin/python
import sys
import os
import MySQLdb

if len(sys.argv) != 4:
  print "Usage: %s dump-file username password" % sys.argv[0]
  exit(1)

input, username, password = sys.argv[1:]

# Create database
c = MySQLdb.connect(host = "localhost", user = username, passwd = password)
cursor = c.cursor()
cursor.execute("CREATE DATABASE __temp_wlanlj_sanitize")

# Import stuff
os.system("sed -i 's/^CREATE DATABASE/--/g' %s" % input)
os.system("sed -i 's/^USE/--/g' %s" % input)
os.system("mysql -u %s --password=%s __temp_wlanlj_sanitize < %s" % (username, password, input))

cursor.execute("UPDATE __temp_wlanlj_sanitize.account_useraccount SET vpn_password = 'XXX', phone = '5551234'")
cursor.execute("UPDATE __temp_wlanlj_sanitize.auth_user SET password = ''")
cursor.execute("UPDATE __temp_wlanlj_sanitize.generator_profile SET root_pass = 'XXX'")
cursor.execute("DELETE FROM __temp_wlanlj_sanitize.django_session")
cursor.close()
c.commit()
c.close()

# Export stuff
os.system("mysqldump -u %s --password=%s __temp_wlanlj_sanitize > DUMP-sanitized.sql" % (username, password))

# Drop database
c = MySQLdb.connect(host = "localhost", user = username, passwd = password)
cursor = c.cursor()
cursor.execute("DROP DATABASE __temp_wlanlj_sanitize")
cursor.close()
c.close()

