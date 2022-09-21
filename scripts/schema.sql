create table if not exists transaction
(
    id               int auto_increment        primary key,
    transaction_date date         null,
    title            varchar(200) null,
    payee            varchar(200) null,
    amount           float        null,
    category         varchar(50)  null
);

