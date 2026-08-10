from app.core.health import check_database


if __name__ == "__main__":
    print("Database:", check_database())