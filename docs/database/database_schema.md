# Wikipedle Database Design Documentation

## Overview

The Wikipedle application uses SQLite database to store user data, game scores, and social relationships. This document describes the initial database design.

## Database Schema

### User System

Wikipedle uses Django's built-in User model for authentication and extends it with the UserProfile model.

#### User Table (Django built-in)

| Field Name | Type | Description |
|------------|------|-------------|
| id | Integer | Primary key |
| username | String | Username |
| email | String | Email address |
| password | String | Password (encrypted) |
| date_joined | DateTime | Registration date |
| is_active | Boolean | Whether the account is active |
| is_staff | Boolean | Whether the user is an admin |

#### UserProfile Table

| Field Name | Type | Description |
|------------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to User table |
| current_streak | Integer | Current consecutive login days |
| max_streak | Integer | Maximum consecutive login days |
| last_played_date | Date | Last game date |

### Game Data

#### DailyScore Table

| Field Name | Type | Description |
|------------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to User table |
| date | Date | Game date |
| score | Integer | Score |
| time_taken | Integer | Time taken (seconds) |
| guesses | Integer | Number of guesses |
| completed | Boolean | Whether the game was completed |

### Social Features

#### Friendship Table

| Field Name | Type | Description |
|------------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to User table |
| friend_id | Integer | Foreign key to User table |
| created_at | DateTime | Time when friendship was established |

## Table Relationships

- User and UserProfile: One-to-one relationship
- User and DailyScore: One-to-many relationship (one user can have multiple daily score records)
- User and Friendship: One-to-many relationship (one user can have multiple friends)

## Constraints

- UserProfile has a one-to-one relationship with User, each user can only have one profile
- The combination of (user_id, date) in the DailyScore table must be unique, ensuring each user has only one score record per day
- The combination of (user_id, friend_id) in the Friendship table must be unique, preventing duplicate friendship relationships

## Indexing Strategy

- Indexes on the username and email fields in the User table to speed up login and lookup
- Composite index on user_id and date fields in the DailyScore table to speed up queries of user history
- Index on the user_id field in the Friendship table to speed up friend list queries

## Future Plans

The database design will iterate as the project progresses, potentially adding:
- Detailed game history data
- Article cache table
- Leaderboard cache table