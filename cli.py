from pymongo import MongoClient
import click

client = MongoClient('localhost', 27017)
users = client.vaccineNotifier.users

@click.group()
def cli():
    pass

@cli.command()
def user_count():
    active = users.count_documents({ "active": True })
    inactive = users.count_documents({ "active": False })
    print("Active: "  + str(active))
    print("Inactive: " + str(inactive))

if __name__ == "__main__":
    cli()
