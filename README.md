
# Bank Marketing Project - Database Schema

## Tables Overview

### 1. **bank_base** 
The base table containing all the data before splitting into dimension and fact tables. It includes raw information from the `bank.csv`.

| Column        | Data Type | Description                                                |
|---------------|-----------|------------------------------------------------------------|
| fact_id       | INT       | Surrogate key, unique for each row                         |
| age           | INT       | Age of the customer                                        |
| job           | STRING    | Job type of the customer                                   |
| marital       | STRING    | Marital status                                             |
| education     | STRING    | Education level                                            |
| credit_default| STRING    | Whether the customer has credit_default                    |
| housing       | STRING    | Housing status                                             |
| loan          | STRING    | Loan status                                                |
| contact       | STRING    | Contact information                                        |
| month         | STRING    | Month of the contact                                       |
| day           | INT       | Day of the contact                                         |
| duration      | INT       | Duration of the contact                                    |
| campaign      | INT       | Campaign information                                       |
| pdays         | INT       | Number of days passed after the last contact               |
| previous      | INT       | Number of contacts performed before this one               |
| poutcome      | STRING    | Outcome of the previous marketing campaign                  |
| deposit       | STRING    | Whether the customer subscribed to the deposit product     |

### 2. **client**
Client dimension table which includes client-specific attributes.

| Column           | Data Type | Description                                              |
|------------------|-----------|----------------------------------------------------------|
| client_id        | INT       | Surrogate key for the client                             |
| fact_id          | INT       | Foreign key, references `bank_base.fact_id`              |
| age              | INT       | Age of the client                                        |
| job              | STRING    | Job type of the client                                   |
| marital          | STRING    | Marital status                                           |
| education        | STRING    | Education level                                          |
| credit_default   | STRING    | Whether the client has credit_default                    |
| housing          | STRING    | Housing status                                           |
| loan             | STRING    | Loan status                                              |

### 3. **contact**
Contact dimension table with information about contact details.

| Column        | Data Type | Description                                              |
|---------------|-----------|----------------------------------------------------------|
| contact_id    | INT       | Surrogate key for the contact                            |
| fact_id       | INT       | Foreign key, references `bank_base.fact_id`              |
| contact       | STRING    | Contact information                                      |
| month         | STRING    | Month of the contact                                     |
| day           | INT       | Day of the contact                                       |
| duration      | INT       | Duration of the contact                                  |

### 4. **campaign**
Campaign dimension table with marketing campaign-related data.

| Column        | Data Type | Description                                              |
|---------------|-----------|----------------------------------------------------------|
| campaign_id   | INT       | Surrogate key for the campaign                           |
| fact_id       | INT       | Foreign key, references `bank_base.fact_id`              |
| campaign      | INT       | Campaign identifier                                      |
| pdays         | INT       | Number of days passed after the last contact             |
| previous      | INT       | Number of previous campaigns                             |
| poutcome      | STRING    | Outcome of the previous campaign                         |

### 5. **marketing**
Fact table that consolidates data from dimension tables and indicates subscription status.

| Column          | Data Type | Description                                              |
|-----------------|-----------|----------------------------------------------------------|
| fact_id         | INT       | Surrogate key, references `bank_base.fact_id`            |
| client_id       | INT       | Foreign key, references `client.client_id`               |
| contact_id      | INT       | Foreign key, references `contact.contact_id`             |
| campaign_id     | INT       | Foreign key, references `campaign.campaign_id`           |
| subscribed      | STRING    | Indicates if the customer subscribed to the deposit      |

## Relationships

- **bank_base** table serves as the base for all other tables, providing a unique `fact_id` for each row.
- The **client**, **contact**, and **campaign** tables are dimension tables that link to the **marketing** table.
- The **marketing** table stores the relationships between clients, their contact details, and the campaigns they are associated with.

