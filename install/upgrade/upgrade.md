## INFO
From 6.6.0 on the database update script can take care of database changes,
even over multiple versions. A backup is made before changes happen. You still
should read the upgrade notes about important information.

**Limitations using the database update script**
* This should only be done within the official **main** branch of OpenAtlas
* If the database owner is not called **openatlas** (default) the SQL files need
  to be updated accordingly before

**How to upgrade**

This upgrade example is written for a Linux system. First update the code base,
then run the database upgrade script, then restart Apache:

    git pull origin main
    sudo python3 install/upgrade/database_upgrade.py
    sudo service apache2 restart

### 8.1.x to 8.2.0

There is no database update for this release but new node packages are needed:

    cd openatlas/static
    npm install

### 8.0.x to 8.1.0
8.1.0.sql is needed but will be taken care of by the database upgrade script.

New node packages are needed:

    cd openatlas/static
    npm install

#### IIIF related clean up
If you followed our Debian install instruction: although it works you can
follow these instructions to avoid error and warn messages in your logs:

* Replace **Location** with **Directory** (2 times) in
**/etc/apache2/mods-available/iipsrv.conf**, see **install/iipsrv.conf** for an
updated example
* Disable systemd to try starting the IIPImage server because it's already
started via Apache


    sudo systemctl disable iipsrv.service

### 7.17.x to 8.0.0
This is a major upgrade which utilizes newer versions of underlying software.
Please consult the install.md about installation. In case you are using a
Debian system, feel free to use our own upgrade notes from the issue
description: https://redmine.openatlas.eu/issues/2038, which is already
tested.

8.0.0.sql is needed but will be taken care of by the database upgrade script.

#### Breaking changes
**Removal of frontend content management**

Because the new presentation site functionality doesn't require content
management in the backend anymore, this functionality was removed.
In case older frontend versions are still in use they would have to be
switched to the new one (OpenAtlas Discovery) or manually adapted.

**New stable API version 0.4**

The current stable API version is **0.4**. Support for API versions **0.3**
is dropped with this release including the frontend content queries mentioned
above.
