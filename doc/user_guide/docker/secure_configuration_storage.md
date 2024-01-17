# Secure Configuration Storage

Most of the examples in the Exasol AI-Lab require a connection to an Exasol database. Additionally some show cases will interact with cloud services which require additional configuration items, URL endpoints, credentials, etc.

To keep all these configuration options accross multiple sessions, Exasol AI-Lab offers a _Secure Configuration Storage_ (SCS).

## Background

The Secure Configuration Storage is based on [coleifer/sqlcipher3](https://github.com/coleifer/sqlcipher3) which uses an encrypted version of an SQLite database. The database is stored in an ordinary, yet encrypted, file and allows to store credentials and other configuration strings in a simple key-value style.

Access to the SCS is encapsulated by a Python library to avoid problems and simplify usage as much as possible.

When using the same file then you can reuse all your configurations and credentials in each session with Exasol AI-Lab while still staying secure as the file is encrypted with a master password that is only known to you.

When file initially does not exist then Exasol AI-Lab will ask you for this master password. In each future session you only need to type in this master password again in order to access the configuration strings stored in previous sessions.

See [Managing User Data](user_data.md) for instructions about how to
* Save the SCS peristently
* Reuse the SCS in future sessions
* Create a backup of the SCS
* Restore the SCS from a backup
