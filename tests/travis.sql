CREATE DATABASE sbtest IF NOT EXISTS;
CREATE TABLE sbtest.test (id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT, uuid VARCHAR(36) NOT NULL DEFAULT '', PRIMARY KEY(id)) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COMMENT='test table';
INSERT INTO sbtest.test(uuid) VALUES('d065af4b-affb-4333-9ebc-789623c9b39b');
INSERT INTO sbtest.test(uuid) VALUES('f5db6916-841e-4fa5-bf1d-afeb4fd31da5');
INSERT INTO sbtest.test(uuid) VALUES('6f312eed-7944-4a7d-844e-67c8ee596587');
INSERT INTO sbtest.test(uuid) VALUES('f7d66740-1f42-4146-8622-c4ef6f42b311');
INSERT INTO sbtest.test(uuid) VALUES('982708ad-2516-41c2-bab9-fd459cf7bf2c');
INSERT INTO sbtest.test(uuid) VALUES('9540c0e6-9983-42a6-a050-9803f992b2ce');
INSERT INTO sbtest.test(uuid) VALUES('14b3abce-f4c5-425f-9190-8a2bfa79a77d');
INSERT INTO sbtest.test(uuid) VALUES('6f353309-82bb-4d3c-b39c-20a366d3b3c2');
INSERT INTO sbtest.test(uuid) VALUES('c8830f48-777c-43cf-9ae0-9a1fbd84217f');
INSERT INTO sbtest.test(uuid) VALUES('564a13ba-3bf4-4642-ba92-d36f8ce6e812');
INSERT INTO sbtest.test(uuid) VALUES('97b8d454-7c8e-4a6a-b0a4-1f1864636d61');

CREATE USER 'tester'@'localhost' IDENTIFIED BY 'Rae9nie3pheevoquai3aeh';
GRANT ALL PRIVILEGES ON sbtest.* TO 'tester'@'localhost';
FLUSH PRIVILEGES;
