# Secure Configuration Storage

Most of the examples in the Exasol AI-Lab require a connection to an Exasol database. Additionally some show cases will interact with cloud services which require additional configuration items, URL endpoints, credentials, etc.

To keep all these configuration options accross multiple sessions and secure, the Exasol AI-Lab offers a _Secure Configuration Storage_ (SCS).

The Secure Configuration Storage is based on [coleifer/sqlcipher3](https://github.com/coleifer/sqlcipher3) which uses an encrypted version of an SQLite database. The database is stored in an ordinary, yet encrypted, file and allows to store credentials and other configuration strings in a simple key-value style.

Access to the SCS is encapsulated by a Python library to simplify usage as much as possible.

When using the same file, you can reuse all your configurations and credentials in each AI-Lab session while still staying secure as the file is encrypted with a master password that is only known to you.

When the file initially does not exist then the AI-Lab will
* Ask you for a new master password
* Create the file
* Encrypt the file with the master password

In each future session AI-Lab will
* Ask you again for the master password
* Use it to unlock and access the configuration strings stored in previous sessions.

See [Managing User Data](managing_user_data.md) for instructions about how to
* Save the SCS peristently
* Reuse the SCS in future sessions
* Create a backup of the SCS
* Restore the SCS from a backup
