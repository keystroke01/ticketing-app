CREATE TABLE "STATUS"(
	"STATUS_ID" INTEGER NOT NULL UNIQUE,
	"CODE" TEXT NOT NULL,
	"DESCRIPTION" TEXT NOT NULL,
	PRIMARY KEY("STATUS_ID" AUTOINCREMENT)
);

CREATE TABLE "TICKET_SEVERITY"(
	"TICKET_SEVERITY_ID" INTEGER NOT NULL UNIQUE,
	"CODE" TEXT NOT NULL,
	"DESCRIPTION" TEXT NOT NULL,
	PRIMARY KEY("TICKET_SEVERITY_ID" AUTOINCREMENT)
);

CREATE TABLE "TICKET_TYPE"(
	"TICKET_TYPE_ID" INTEGER NOT NULL UNIQUE,
	"CODE" TEXT NOT NULL,
	"DESCRIPTION" TEXT NOT NULL,
	PRIMARY KEY("TICKET_TYPE_ID" AUTOINCREMENT)
);


CREATE TABLE "TICKETS" (
	"TICKET_ID"	INTEGER NOT NULL UNIQUE,
	"TITLE"	TEXT NOT NULL,
	"DESCRIPTION"	TEXT,
	"REPORTED_DATE"	TEXT,
	"CLOSED_DATE"	TEXT,
	"TICKET_TYPE_ID" INTEGER,
	"TICKET_SEVERITY_ID" INTEGER,
	"STATUS_ID" INTEGER,
	PRIMARY KEY("TICKET_ID" AUTOINCREMENT)
	FOREIGN KEY ("TICKET_TYPE_ID") REFERENCES "TICKET_TYPE"("TICKET_TYPE_ID"),
	FOREIGN KEY ("TICKET_SEVERITY_ID") REFERENCES "TICKET_SEVERITY"("TICKET_SEVERITY_ID"),
	FOREIGN KEY ("STATUS_ID") REFERENCES "STATUS"("STATUS_ID")
);

CREATE TABLE "TICKET_ATTACHMENTS"(
	"ATTACHMENT_ID" INTEGER NOT NULL UNIQUE,
	"ATTACHMENT_PATH" TEXT,
	"TICKET_ID" INTEGER,
	PRIMARY KEY("ATTACHMENT_ID" AUTOINCREMENT),
	FOREIGN KEY ("TICKET_ID") REFERENCES "TICKETS"("TICKET_ID")
);

INSERT INTO "STATUS" ("CODE", "DESCRIPTION") VALUES ('O', 'Open');
INSERT INTO "STATUS" ("CODE", "DESCRIPTION") VALUES ('P', 'In Progress');
INSERT INTO "STATUS" ("CODE", "DESCRIPTION") VALUES ('A', 'Awaiting Deployment');
INSERT INTO "STATUS" ("CODE", "DESCRIPTION") VALUES ('C', 'Closed');

INSERT INTO "TICKET_SEVERITY" ("CODE", "DESCRIPTION") VALUES ('MIN', 'Minor');
INSERT INTO "TICKET_SEVERITY" ("CODE", "DESCRIPTION") VALUES ('MAJ', 'Major');

INSERT INTO "TICKET_TYPE" ("CODE", "DESCRIPTION") VALUES ('B', 'Bug');
INSERT INTO "TICKET_TYPE" ("CODE", "DESCRIPTION") VALUES ('UA', 'User Assistance');



CREATE VIEW "V_TICKETS" AS 
	SELECT
	CAST(T.TICKET_ID AS TEXT) "ID",
	T.TITLE, 
	T.DESCRIPTION,
	TY.DESCRIPTION "TYPE",
	S.DESCRIPTION "SEVERITY",
	ST.DESCRIPTION "STATUS",
	T.REPORTED_DATE "REPORTED DATE",
	T.CLOSED_DATE "CLOSED DATE"	
	FROM TICKETS T
	LEFT JOIN TICKET_SEVERITY S ON T.TICKET_SEVERITY_ID = S.TICKET_SEVERITY_ID
	LEFT JOIN TICKET_TYPE TY ON T.TICKET_TYPE_ID = TY.TICKET_TYPE_ID
	LEFT JOIN STATUS ST ON T.STATUS_ID = ST.STATUS_ID
;