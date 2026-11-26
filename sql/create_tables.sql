-- 1. Support Logs: Table DDL, COPY & Verify
CREATE TABLE IF NOT EXISTS public.support_logs (
    timestamp       TIMESTAMP,
    log_level       VARCHAR(20),
    component       VARCHAR(100),
    ticket_id       VARCHAR(50),
    session_id      VARCHAR(50),
    ip              VARCHAR(45),
    response_time   BIGINT,
    cpu             DOUBLE PRECISION,
    event_type      VARCHAR(50),
    error           BOOLEAN,
    user_agent      VARCHAR(300),
    message         VARCHAR(1000),
    debug           VARCHAR(1000)
);

COPY public.support_logs
FROM 's3://care-plus-datalake/support-logs/processed/'
IAM_ROLE 'arn:aws:iam::<AWS_ACCOUNT_ID>:role/service-role/<REDSHIFT_ACCESS_ROLE>'
FORMAT AS PARQUET
REGION 'ap-southeast-2';

SELECT COUNT(*) FROM public.support_logs;
SELECT * FROM public.support_logs LIMIT 10;



-- 2. Support Tickets: Table DDL, COPY & Verify
CREATE TABLE IF NOT EXISTS public.support_tickets (
    ticket_id        VARCHAR(50),
    created_at       TIMESTAMP,
    resolved_at      TIMESTAMP,
    agent            VARCHAR(100),
    priority         VARCHAR(20),
    num_interactions BIGINT,
    issuecat         VARCHAR(100),
    channel          VARCHAR(50),
    status           VARCHAR(20)
);

COPY public.support_tickets
FROM 's3://care-plus-datalake/support-tickets/processed/'
IAM_ROLE 'arn:aws:iam::<AWS_ACCOUNT_ID>:role/service-role/<REDSHIFT_ACCESS_ROLE>'
FORMAT AS PARQUET
REGION 'ap-southeast-2';

SELECT COUNT(*) FROM public.support_tickets;
SELECT * FROM public.support_tickets LIMIT 10;