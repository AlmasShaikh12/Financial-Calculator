from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Load Excel file
df = pd.read_excel("Pune_5x5_Villages_with_businesses-3.xlsx")


@app.get("/")
def home():
    return {"message": "AI Business Advisor Backend is running"}


@app.get("/columns")
def get_columns():
    return {"columns": df.columns.tolist()}


@app.get("/villages")
def get_villages():

    village_column = "Village Name"

    villages = (
        df[village_column]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    villages.sort()

    return {"villages": villages}


@app.get("/village/{village_name}")
def get_village(village_name: str):

    village_column = "Village Name"

    result = df[
        df[village_column]
        .astype(str)
        .str.strip()
        .str.lower()
        == village_name.strip().lower()
    ]

    if result.empty:
        return {"error": "Village not found"}

    return result.iloc[0].fillna("").to_dict()


@app.get("/businesses")
def get_businesses():

    business_columns = [
        "Sample Local Business 1",
        "Sample Local Business 2",
        "Sample Local Business 3",
        "Sample Local Business 4",
        "Sample Local Business 5",
        "Sample Local Business 6",
        "Sample Local Business 7",
        "Sample Local Business 8"
    ]

    businesses = set()

    for column in business_columns:
        if column in df.columns:
            for value in df[column].dropna():
                businesses.add(str(value).strip())

    return {"businesses": sorted(businesses)}
@app.get("/village/{village_name}/businesses")
def get_village_businesses(village_name: str):

    village_column = "Village Name"

    result = df[
        df[village_column]
        .astype(str)
        .str.strip()
        .str.lower()
        == village_name.strip().lower()
    ]

    if result.empty:
        return {"error": "Village not found"}

    business_columns = [
        "Sample Local Business 1",
        "Sample Local Business 2",
        "Sample Local Business 3",
        "Sample Local Business 4",
        "Sample Local Business 5",
        "Sample Local Business 6",
        "Sample Local Business 7",
        "Sample Local Business 8"
    ]

    businesses = []

    for column in business_columns:
        if column in df.columns:
            value = result.iloc[0][column]

            if pd.notna(value) and str(value).strip():
                businesses.append(str(value).strip())

    return {
        "village": village_name,
        "existing_businesses": businesses
    }
@app.get("/village/{village_name}/population")
def get_village_population(village_name: str):

    result = df[
        df["Village Name"]
        .astype(str)
        .str.strip()
        .str.lower()
        == village_name.strip().lower()
    ]

    if result.empty:
        return {"error": "Village not found"}

    row = result.iloc[0]

    # Find columns even if they contain extra spaces
    columns = {}

    for col in df.columns:
        clean_col = " ".join(str(col).split()).strip().lower()

        if clean_col == "total households":
            columns["households"] = col

        elif clean_col == "total population of village":
            columns["population"] = col

        elif clean_col == "total male population of village":
            columns["male"] = col

        elif clean_col == "total female population of village":
            columns["female"] = col

    return {
        "village": row["Village Name"],
        "households": row[columns["households"]],
        "total_population": row[columns["population"]],
        "male_population": row[columns["male"]],
        "female_population": row[columns["female"]]
    }