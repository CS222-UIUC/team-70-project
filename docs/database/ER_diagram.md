# Wikipedle Entity Relationship Diagram

## ER Diagram Description

The following diagram shows the main entities and their relationships in the Wikipedle application:

```
+-------------+       +-----------------+       +-------------+
|    User     |       |   UserProfile   |       | DailyScore  |
+-------------+       +-----------------+       +-------------+
| id          |<----->| id              |       | id          |
| username    |       | user_id         |       | user_id     |
| email       |       | current_streak  |       | date        |
| password    |       | max_streak      |       | score       |
| date_joined |       | last_played_date|       | time_taken  |
+-------------+       +-----------------+       | guesses     |
      ^                                         | completed   |
      |                                         +-------------+
      |                                                ^
      |                                                |
      +------------------------------------------------+
      |
      |
+-------------+
| Friendship  |
+-------------+
| id          |
| user_id     |
| friend_id   |
| created_at  |
+-------------+


## Relationship Description

1. **User and UserProfile**: One-to-one relationship
   - Each User entity corresponds to one UserProfile entity
   - Relationship is implemented through the user_id foreign key in the UserProfile table

2. **User and DailyScore**: One-to-many relationship
   - One User can have multiple DailyScore records
   - Relationship is implemented through the user_id foreign key in the DailyScore table

3. **User and Friendship**: Many-to-many relationship
   - One User can establish friendship relationships with multiple other Users
   - Relationship is implemented through the Friendship table, which contains two foreign keys: user_id and friend_id, both pointing to the User table

## Business Rules

- A UserProfile is automatically created when a user registers
- Each user can have only one game score record per day
- Friendship relationships are bidirectional, but require two records in the database
