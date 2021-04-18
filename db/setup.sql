CREATE ROLE IF NOT EXISTS tlis_sysadmin WITH ADMIN `root`@`%`;

GRANT ALL PRIVILEGES ON *.* TO TO tlis_sysadmin;

CREATE ROLE IF NOT EXISTS tlis_manager WITH ADMIN `root`@`%`;

GRANT INSERT, DELETE, UPDATE, SELECT ON TLIS.* TO TO tlis_manager;

CREATE ROLE IF NOT EXISTS tlis_tech WITH ADMIN `root`@`%`;

GRANT USAGE, INSERT, DELETE, UPDATE, SELECT ON TLIS.asset_types, TLIS.assets, TLIS.customers, TLIS.transaction_types, TLIS.transactions_in, TLIS.transactions_out TO tlis_tech;
