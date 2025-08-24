from prefect import flow, task

@task
def extract_files():
    pass  # TODO: parse JSON/CSV/XML and write to Bronze(data/bronze/)

@task
def extract_api():
    pass  # TODO: fetch paginated API data and write to Bronze(data/bronze/)

@task
def extract_web():
    pass  # TODO: scrape dynamic page and write to Bronze(data/bronze/)

@task
def spark_bronze_to_silver():
    pass  # TODO: call Spark job

@task
def validate_silver():
    pass  # TODO: run validation and write rejected

@task
def load_silver_to_db():
    pass  # TODO: upsert into Postgres

@task
def build_gold():
    pass  # TODO: compute aggregates and load to DB

@flow
def pipeline():
    # Wire your tasks in order here.
    pass

if __name__ == "__main__":
    pipeline()
