BEGIN TRANSACTION;
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    act_id INTEGER UNIQUE,
    datetime VARCHAR(1023),
    comment VARCHAR(1023),
    description VARCHAR(1023),
    operation VARCHAR(1023),
    type VARCHAR(1023),
    uzer VARCHAR(1023)
);
INSERT INTO transactions VALUES(1,63258,'2024-11-19T17:12:50Z',NULL,'Generic Record was updated','UPDATE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(2,63259,'2024-11-19T17:13:42Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(3,63260,'2024-11-19T17:14:34Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(4,63261,'2024-11-19T18:58:18Z',NULL,'Alias Record was added','ADD_ALIAS_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(5,63262,'2024-11-19T19:06:15Z',NULL,'Alias Record was deleted','DELETE_ALIAS_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(6,63263,'2024-11-19T19:09:47Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(7,63264,'2024-11-22T18:40:24Z',NULL,'Generic Record was renamed','RENAME_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(8,63265,'2024-11-22T19:04:15Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(9,63266,'2024-11-22T19:04:48Z',NULL,'Generic Record was updated','UPDATE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(10,63267,'2024-11-22T19:57:27Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(11,63268,'2024-11-22T20:04:38Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(12,63269,'2024-11-22T20:15:17Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(13,63270,'2024-11-26T17:34:38Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(14,63271,'2024-11-26T17:34:38Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(15,63272,'2024-11-26T17:34:38Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(16,63273,'2024-11-26T17:34:38Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(17,63274,'2024-11-26T17:34:39Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(18,63275,'2024-11-26T17:34:39Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(19,63278,'2024-11-26T17:37:04Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(20,63279,'2024-11-26T17:37:04Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(21,63280,'2024-11-26T17:37:04Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(22,63281,'2024-11-28T18:14:04Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(23,63282,'2024-11-28T18:20:40Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(24,63283,'2024-11-28T18:25:07Z',NULL,'Generic Record was updated','UPDATE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(25,63284,'2024-11-28T18:26:11Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(26,63285,'2024-11-28T18:26:36Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(27,63286,'2024-11-28T18:34:26Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(28,63287,'2024-11-28T18:34:50Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(29,63288,'2024-11-28T18:42:17Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(30,63290,'2024-11-28T18:44:05Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(31,63291,'2024-11-28T18:44:33Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(32,63292,'2024-11-28T18:45:45Z',NULL,'Generic Record was deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(33,63294,'2024-11-28T18:51:43Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(34,63295,'2024-11-28T18:52:02Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(35,63297,'2024-11-28T19:42:46Z',NULL,'Several Resource Records were deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(36,63298,'2024-11-28T19:44:38Z',NULL,'Generic Record was updated','UPDATE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(37,63299,'2024-11-28T19:45:54Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(38,63300,'2024-11-28T19:46:08Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(39,63301,'2024-11-28T19:46:23Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(40,63302,'2024-11-28T19:47:42Z',NULL,'Several Resource Records were deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(41,63303,'2024-11-28T20:36:13Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(42,63304,'2024-11-28T20:36:31Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(43,63305,'2024-11-28T20:36:46Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(44,63306,'2024-11-28T20:39:33Z',NULL,'Several Resource Records were deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(45,63307,'2024-11-28T20:47:20Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(46,63308,'2024-11-28T20:48:21Z',NULL,'Several Resource Records were deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(47,63309,'2024-11-28T20:57:23Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(48,63310,'2024-11-28T20:57:39Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(49,63311,'2024-11-28T21:12:22Z',NULL,'Several Resource Records were deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(50,63312,'2024-11-28T21:17:43Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(51,63313,'2024-11-28T21:17:56Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(52,63314,'2024-11-28T21:18:23Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(53,63315,'2024-11-28T21:22:03Z',NULL,'Several Resource Records were deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(54,63316,'2024-11-28T21:24:27Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(55,63317,'2024-11-28T21:24:41Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(56,63318,'2024-11-28T21:25:13Z',NULL,'Several Resource Records were deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(57,63319,'2024-11-28T21:28:19Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(58,63320,'2024-11-28T21:28:36Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(59,63321,'2024-11-28T21:28:47Z',NULL,'Generic Record was added','ADD_GENERIC_RECORD',NULL,'sutherl4');
INSERT INTO transactions VALUES(60,63322,'2024-11-28T21:29:21Z',NULL,'Several Resource Records were deleted','DELETE_GENERIC_RECORD',NULL,'sutherl4');
CREATE TABLE last_run (
    id SERIAL PRIMARY KEY,
    isodate VARCHAR(1023),
    unixtime INTEGER
);
INSERT INTO last_run VALUES(1,'2024-11-28T21:29:27Z',1732829367);
CREATE TABLE log (
    id SERIAL PRIMARY KEY,
    isodate VARCHAR(1023) NOT NULL,  -- ISO 8601 date format with milliseconds E.g. 2024-11-21T14:21:53+00:00
    unixtime INTEGER,       -- seconds since the epoch
    transaction_ids VARCHAR(1023),   -- CSV representation of the transaction ids which occurred since the last scan
    changed_zones VARCHAR(1023)      -- CSV representation of changed zones since last scan
);
INSERT INTO log VALUES(1,'2024-11-22T19:54:36.339132+00:00',1732305276,'','');
INSERT INTO log VALUES(2,'2024-11-22T19:55:03.767966+00:00',1732305303,'','');
INSERT INTO log VALUES(3,'2024-11-22T20:02:53.719134+00:00',1732305773,'[]','');
INSERT INTO log VALUES(4,'2024-11-22T20:05:03.123771+00:00',1732305903,'[63268]','privatelink_openai_azure_com.000');
INSERT INTO log VALUES(5,'2024-11-22T20:14:28.037314+00:00',1732306468,'[]','');
INSERT INTO log VALUES(6,'2024-11-22T20:15:23.335874+00:00',1732306523,'[63269]','privatelink_openai_azure_com.000');
INSERT INTO log VALUES(7,'2024-11-22T20:18:15.937892+00:00',1732306695,'[]','');
INSERT INTO log VALUES(8,'2024-11-22T20:26:49.014741+00:00',1732307209,'[]','');
INSERT INTO log VALUES(9,'2024-11-22T21:36:50.342658+00:00',1732311410,'[]','');
INSERT INTO log VALUES(10,'2024-11-24T19:43:29Z',1732477409,'[]','');
INSERT INTO log VALUES(11,'2024-11-24T19:43:55Z',1732477435,'[]','');
INSERT INTO log VALUES(12,'2024-11-25T14:37:45Z',1732545465,'','');
INSERT INTO log VALUES(13,'2024-11-28T15:43:21Z',1732808601,'[63270, 63271, 63272, 63273, 63274, 63275, 63278, 63279, 63280]','["privatelink_openai_azure_com.278", "privatelink_openai_azure_com.278", "privatelink_openai_azure_com.278", "privatelink_openai_azure_com.278", "privatelink_openai_azure_com.278", "privatelink_openai_azure_com.278", "privatelink_openai_azure_com.278", "privatelink_openai_azure_com.278", "privatelink_openai_azure_com.278"]');
INSERT INTO log VALUES(14,'2024-11-28T17:58:51Z',1732816731,'','');
INSERT INTO log VALUES(15,'2024-11-28T18:00:51Z',1732816851,'','');
INSERT INTO log VALUES(16,'2024-11-28T18:02:19Z',1732816939,'','');
INSERT INTO log VALUES(17,'2024-11-28T18:03:07Z',1732816987,'','');
INSERT INTO log VALUES(18,'2024-11-28T18:03:09Z',1732816989,'','');
INSERT INTO log VALUES(19,'2024-11-28T18:16:42Z',1732817802,'[63281]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(20,'2024-11-28T18:17:10Z',1732817830,'','');
INSERT INTO log VALUES(21,'2024-11-28T18:20:50Z',1732818050,'[63282]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(22,'2024-11-28T18:24:46Z',1732818286,'','');
INSERT INTO log VALUES(23,'2024-11-28T18:25:18Z',1732818318,'[63283]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(24,'2024-11-28T18:26:43Z',1732818403,'[63284, 63285]','["privatelink_openai_azure_com.000", "privatelink_openai_azure_com.278"]');
INSERT INTO log VALUES(25,'2024-11-28T18:31:09Z',1732818669,'','');
INSERT INTO log VALUES(26,'2024-11-28T18:34:59Z',1732818899,'[63286, 63287]','["privatelink_openai_azure_com.278"]');
INSERT INTO log VALUES(27,'2024-11-28T18:41:30Z',1732819290,'','');
INSERT INTO log VALUES(28,'2024-11-28T18:42:32Z',1732819352,'[63288]','["privatelink_openai_azure_com.278"]');
INSERT INTO log VALUES(29,'2024-11-28T18:43:03Z',1732819383,'','');
INSERT INTO log VALUES(30,'2024-11-28T18:43:32Z',1732819412,'','');
INSERT INTO log VALUES(31,'2024-11-28T18:44:40Z',1732819480,'[63290, 63291]','["privatelink_openai_azure_com.278"]');
INSERT INTO log VALUES(32,'2024-11-28T18:45:58Z',1732819558,'[63292]','["privatelink_openai_azure_com.278"]');
INSERT INTO log VALUES(33,'2024-11-28T18:46:26Z',1732819586,'','');
INSERT INTO log VALUES(34,'2024-11-28T18:48:37Z',1732819717,'','');
INSERT INTO log VALUES(35,'2024-11-28T18:57:19Z',1732820239,'[63294, 63295]','["privatelink_openai_azure_com.278"]');
INSERT INTO log VALUES(36,'2024-11-28T18:58:10Z',1732820290,'','');
INSERT INTO log VALUES(37,'2024-11-28T18:58:36Z',1732820316,'','');
INSERT INTO log VALUES(38,'2024-11-28T19:42:09Z',1732822929,'','');
INSERT INTO log VALUES(39,'2024-11-28T19:42:52Z',1732822972,'[63297, 63297]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(40,'2024-11-28T19:44:44Z',1732823084,'[63298]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(41,'2024-11-28T19:46:35Z',1732823195,'[63299, 63300, 63301]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(42,'2024-11-28T19:47:48Z',1732823268,'[63302, 63302, 63302]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(43,'2024-11-28T20:35:22Z',1732826122,'','');
INSERT INTO log VALUES(44,'2024-11-28T20:38:01Z',1732826281,'[63303, 63304, 63305]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(45,'2024-11-28T20:39:38Z',1732826378,'[63306]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(46,'2024-11-28T20:47:44Z',1732826864,'[63307]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(47,'2024-11-28T20:48:28Z',1732826908,'[63308]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(48,'2024-11-28T20:57:00Z',1732827420,'','');
INSERT INTO log VALUES(49,'2024-11-28T21:11:32Z',1732828292,'[63309, 63310]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(50,'2024-11-28T21:12:43Z',1732828363,'[63311]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(51,'2024-11-28T21:17:17Z',1732828637,'','');
INSERT INTO log VALUES(52,'2024-11-28T21:20:50Z',1732828850,'[63312, 63313, 63314]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(53,'2024-11-28T21:22:09Z',1732828929,'[63315]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(54,'2024-11-28T21:24:06Z',1732829046,'','');
INSERT INTO log VALUES(55,'2024-11-28T21:24:45Z',1732829085,'[63316, 63317]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(56,'2024-11-28T21:27:34Z',1732829254,'[63318]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(57,'2024-11-28T21:28:52Z',1732829332,'[63319, 63320, 63321]','["privatelink_openai_azure_com.000"]');
INSERT INTO log VALUES(58,'2024-11-28T21:29:27Z',1732829367,'[63322]','["privatelink_openai_azure_com.000"]');
CREATE TABLE operations (
    id SERIAL PRIMARY KEY,
    act_id INTEGER,
    rr_id INTEGER,
    op_type VARCHAR(1023),
    bc_type VARCHAR(1023),
    rr_comment VARCHAR(1023),
    rr_hname VARCHAR(1023),
    rr_fqdn VARCHAR(1023),
    rr_type VARCHAR(1023),
    rr_value VARCHAR(1023),
    rr_ttl INTEGER
);
INSERT INTO operations VALUES(1,63318,167112,'DELETE','GenericRecord',NULL,'q000_asdss','q000_asdss.privatelink_openai_azure_com.000','A','10.141.11.22',NULL);
INSERT INTO operations VALUES(2,63318,167113,'DELETE','GenericRecord',NULL,'q000_asdaaa','q000_asdaaa.privatelink_openai_azure_com.000','A','10.141.11.22',NULL);
INSERT INTO operations VALUES(3,63319,167114,'ADD','GenericRecord',NULL,'q000_asdaaaa','q000_asdaaaa.privatelink_openai_azure_com.000','A','10.141.221.31',NULL);
INSERT INTO operations VALUES(4,63320,167115,'ADD','GenericRecord',NULL,'q000_asdaas','q000_asdaas.privatelink_openai_azure_com.000','A','10.141.222.121',NULL);
INSERT INTO operations VALUES(5,63321,167116,'ADD','GenericRecord',NULL,'q000_dds','q000_dds.privatelink_openai_azure_com.000','A','10.141.22.44',NULL);
INSERT INTO operations VALUES(6,63322,167109,'DELETE','GenericRecord',NULL,'q000_asd_dog','q000_asd_dog.privatelink_openai_azure_com.000','A','10.141.11.22',NULL);
INSERT INTO operations VALUES(7,63322,167114,'DELETE','GenericRecord',NULL,'q000_asdaaaa','q000_asdaaaa.privatelink_openai_azure_com.000','A','10.141.221.31',NULL);
INSERT INTO operations VALUES(8,63322,167116,'DELETE','GenericRecord',NULL,'q000_dds','q000_dds.privatelink_openai_azure_com.000','A','10.141.22.44',NULL);
INSERT INTO operations VALUES(9,63322,167115,'DELETE','GenericRecord',NULL,'q000_asdaas','q000_asdaas.privatelink_openai_azure_com.000','A','10.141.222.121',NULL);
COMMIT;
