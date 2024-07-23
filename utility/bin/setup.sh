#! /usr/bin/env bash

docker rm -f dbnetbaan

docker run --name dbnetbaan -e POSTGRES_PASSWORD=1234 -d --rm -p "5432:5432" -e PGDATA=/var/lib/postgresql/data/pgdatanetbaan -v /docker/db:/var/lib/postgresql/data postgres:alpine

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
RETRIES=10
until docker exec -i dbnetbaan pg_isready -U postgres || [ $RETRIES -eq 0 ]; do
  echo "Waiting for PostgreSQL server, $((RETRIES--)) remaining attempts..."
  sleep 2
done

if [ $RETRIES -eq 0 ]; then
  echo "PostgreSQL did not start in time."
  exit 1
fi

echo "setup complete Delete migrations."

docker exec -i dbnetbaan psql -U postgres -d dbnetbaan -c "
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS account_user CASCADE;
DROP TABLE IF EXISTS account_user_groups CASCADE;
DROP TABLE IF EXISTS account_user_user_permissions CASCADE;
DROP TABLE IF EXISTS account_userauth CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS authtoken_token CASCADE;
DROP TABLE auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS django_admin_log CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;
"

echo "Setup complete: Dropped tables."
sleep 2

python manage.py makemigrations
echo "Setup complete: Created migrations."
sleep 2

python manage.py migrate
echo "Setup complete: Applied migrations."
sleep 2




docker exec -i dbnetbaan psql -U postgres -d dbnetbaan -c "
INSERT INTO account_user (
    username, email, password, phone_number, last_login, create_time, update_time, is_deleted, is_active, is_admin, is_staff, is_superuser
) VALUES
    ('user1', 'user1@gmail.com', 'password@1', '09128355701', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE),
    ('user2', 'user2@gmail.com', 'password@2', '09128355702', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE),
    ('user3', 'user3@gmail.com', 'password@3', '09128355703', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE),
    ('user4', 'user4@gmail.com', 'password@4', '09128355704', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE),
    ('user5', 'user5@gmail.com', 'password@5', '09128355705', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE);
"
docker exec -i dbnetbaan psql -U postgres -d dbnetbaan -c "
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(200) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    UNIQUE (title, author, genre)
);
"
docker exec -i dbnetbaan psql -U postgres -d dbnetbaan -c "
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    account_user_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
    FOREIGN KEY (account_user_id) REFERENCES account_user (id) ON DELETE CASCADE,
    CONSTRAINT unique_user_book_review UNIQUE (book_id, account_user_id)
);
"
docker exec -i dbnetbaan psql -U postgres -d dbnetbaan -c "
INSERT INTO books (title, author, genre) VALUES
('Book A1', 'Author 1', 'Adventure'),
('Book A2', 'Author 1', 'Mystery'),
('Book A3', 'Author 1', 'Science Fiction'),
('Book B1', 'Author 2', 'History'),
('Book B2', 'Author 2', 'Romance'),
('Book B3', 'Author 2', 'Science'),
('Book C1', 'Author 3', 'Cooking'),
('Book C2', 'Author 3', 'Gardening'),
('Book C3', 'Author 3', 'Travel'),
('Book D1', 'Author 4', 'Adventure'),
('Book D2', 'Author 4', 'Adventure'),
('Book D3', 'Author 4', 'Adventure'),
('Book E1', 'Author 5', 'Mystery'),
('Book E2', 'Author 5', 'Mystery'),
('Book E3', 'Author 5', 'Mystery'),
('Book F1', 'Author 6', 'Science'),
('Book F2', 'Author 7', 'History'),
('Book F3', 'Author 8', 'Romance'),
('Book F4', 'Author 9', 'Science Fiction'),
('Book F5', 'Author 10', 'Cooking'),
('Book F6', 'Author 11', 'Gardening'),
('Book F7', 'Author 12', 'Travel'),
('Book F8', 'Author 13', 'Education'),
('Book F9', 'Author 14', 'Horror'),
('Book F10', 'Author 15', 'Adventure'),
('Book F11', 'Author 16', 'Mystery'),
('Book F12', 'Author 17', 'Science'),
('Book F13', 'Author 18', 'History'),
('Book F14', 'Author 19', 'Romance'),
('Book F15', 'Author 20', 'Science Fiction'),
('Book F16', 'Author 21', 'Cooking'),
('Book F17', 'Author 22', 'Gardening'),
('Book F18', 'Author 23', 'Travel'),
('Book F19', 'Author 24', 'Education'),
('Book F20', 'Author 25', 'Horror'),
('Book F21', 'Author 6', 'Romance'),
('Book F22', 'Author 7', 'Adventure'),
('Book F23', 'Author 8', 'Mystery'),
('Book F24', 'Author 9', 'Science'),
('Book F25', 'Author 10', 'History'),
('Book F26', 'Author 11', 'Romance'),
('Book F27', 'Author 12', 'Science Fiction'),
('Book F28', 'Author 13', 'Cooking'),
('Book F29', 'Author 14', 'Gardening'),
('Book F30', 'Author 15', 'Travel'),
('Book F31', 'Author 16', 'Education'),
('Book F32', 'Author 17', 'Horror'),
('Book F33', 'Author 18', 'Adventure'),
('Book F34', 'Author 19', 'Mystery'),
('Book F35', 'Author 20', 'Science'),
('Book F36', 'Author 21', 'History'),
('Book F37', 'Author 22', 'Romance'),
('Book F38', 'Author 23', 'Science Fiction'),
('Book F39', 'Author 24', 'Cooking'),
('Book F40', 'Author 25', 'Gardening'),
('Book F41', 'Author 6', 'Travel'),
('Book F42', 'Author 7', 'Education'),
('Book F43', 'Author 8', 'Horror'),
('Book F44', 'Author 9', 'Adventure'),
('Book F45', 'Author 10', 'Mystery'),
('Book F46', 'Author 11', 'Science'),
('Book F47', 'Author 12', 'History'),
('Book F48', 'Author 13', 'Romance'),
('Book F49', 'Author 14', 'Science Fiction'),
('Book F50', 'Author 15', 'Cooking');
"
docker exec -i dbnetbaan psql -U postgres -d dbnetbaan -c "
INSERT INTO reviews (book_id, account_user_id, rating) VALUES
(1, 1, 5),
(2, 1, 4),
(3, 1, 3),
(4, 1, 5),
(5, 1, 2),
(6, 1, 4),
(7, 1, 5),
(8, 1, 3),
(9, 1, 4),
(10, 1, 5),
(11, 2, 3),
(12, 2, 4),
(13, 2, 5),
(14, 2, 2),
(15, 2, 4),
(16, 2, 5),
(17, 2, 3),
(18, 2, 4),
(19, 2, 5),
(20, 2, 2),
(21, 3, 4),
(22, 3, 5),
(23, 3, 3),
(24, 3, 4),
(25, 3, 5),
(26, 3, 2),
(27, 3, 4),
(28, 3, 5),
(29, 3, 3),
(30, 3, 4),
(31, 4, 5),
(32, 4, 2),
(33, 4, 4),
(34, 4, 5),
(35, 4, 3),
(36, 4, 4),
(37, 4, 5),
(38, 4, 2),
(39, 4, 4),
(40, 4, 5),
(41, 5, 3),
(42, 5, 4),
(43, 5, 5),
(44, 5, 2),
(45, 5, 4),
(46, 5, 5),
(47, 5, 3),
(48, 5, 4),
(49, 5, 5),
(50, 5, 2),
(1, 2, 4),
(2, 3, 5),
(3, 4, 3),
(4, 5, 4),
(5, 2, 5),
(6, 3, 3),
(7, 4, 4),
(8, 5, 5),
(9, 3, 2),
(10, 2, 4),
(11, 3, 5),
(12, 4, 3),
(13, 5, 4),
(14, 3, 5),
(15, 4, 3),
(16, 5, 4),
(17, 1, 5),
(18, 4, 2),
(19, 5, 4),
(20, 1, 5);
"
echo "Database setup complete."

echo "Creating superuser..."
python manage.py creat_a_super_user --username PedraKmarimi --email pedram.9060@gmail.com --password qwertyQ@1 --phone_number 09128355747
if [ $? -ne 0 ]; then
  echo "Failed to create superuser."
  exit 1
fi
echo "setup complete creat a super user."
sleep 2

echo "Starting Django development server..."
python manage.py runserver