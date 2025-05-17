from fastapi import FastAPI
import uvicorn
import mlflow 
from pydantic import BaseModel
import numpy as np 
import pandas as pd 

app = FastAPI()

mlflow.set_tracking_uri("http://a7ff29e59272e44458bae980a656cb8f-1038010547.us-east-2.elb.amazonaws.com:5000")
logged_model = 'runs:/ad9dc4ed88d2451bb0995343b1bbfbe6/model'

# Load model as a PyFuncModel.
model = mlflow.pyfunc.load_model(logged_model)

class FlowerPartSize(BaseModel):
    width: float
    length: float

class PredictionRequest(BaseModel):
    sepal: FlowerPartSize
    petal: FlowerPartSize
 
@app.post("/predict")
def predict(request : PredictionRequest): 
    X = pd.DataFrame(
        columns=['sepal.length', 'sepal.width', 'petal.length', 'petal.width'],
        data=
        [
            [request.sepal.length,request.sepal.width, request.petal.length, request.petal.width]
        ]
    )

    y_proba = model.predict(X)

    prediction = int(np.argmax(y_proba))

    return {"flower": prediction}


def main():
    uvicorn.run(app,host="0.0.0.0",port=8000)

if __name__ == "__main__":
    main()
