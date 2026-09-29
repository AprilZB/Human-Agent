DROP TABLE IF EXISTS base_bom;
CREATE TABLE ase_bom (
  om_code varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  product_code varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  component_code varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  quantity decimal(10,2) NOT NULL,
  lt_group varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (om_code, product_code, component_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
