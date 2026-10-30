let
    // Public demo API. Use Get Data > Blank Query > Advanced Editor.
    Source = Json.Document(Web.Contents("https://dummyjson.com/products?limit=10")),
    ProductList = Source[products],
    AsTable = Table.FromList(ProductList, Splitter.SplitByNothing(), {"ProductRecord"}, null, ExtraValues.Error),
    Expanded = Table.ExpandRecordColumn(
        AsTable,
        "ProductRecord",
        {"id", "title", "category", "price", "rating", "stock", "brand"},
        {"API_ProductID", "API_Title", "API_Category", "API_Price", "API_Rating", "API_Stock", "API_Brand"}
    ),
    ChangedTypes = Table.TransformColumnTypes(
        Expanded,
        {
            {"API_ProductID", Int64.Type},
            {"API_Title", type text},
            {"API_Category", type text},
            {"API_Price", type number},
            {"API_Rating", type number},
            {"API_Stock", Int64.Type},
            {"API_Brand", type text}
        }
    )
in
    ChangedTypes
