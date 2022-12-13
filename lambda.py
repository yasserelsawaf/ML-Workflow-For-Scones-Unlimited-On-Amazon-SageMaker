#First Function serialize Image Data
import json
import boto3
import base64
"""{
  "image_data": "",
  "s3_bucket": "sagemaker-us-east-1-310724489955",
  "s3_key": "test/bicycle_s_000059.png",
  "inferences": []
}"""

s3 = boto3.client('s3')

def lambda_handler(event, context):
   """A function to serialize target data from S3"""
   # Get the s3 address from the Step Function event input
   key = event['s3_key']
   bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    boto3.resource('s3').Bucket(bucket).download_file(key,'/tmp/image.png')
    
    # We read the data from a file
   with open("/tmp/image.png", "rb") as f:
       image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
   print("Event:", event.keys())
   return {
       'statusCode': 200,
       'body': {
           "image_data": image_data,
           "s3_bucket": bucket,
           "s3_key": key,
           "inferences": []
           
       }
       
   }

#Second Funtion Classification
import json
import base64
import boto3

# Fill this in with the name of your deployed model
ENDPOINT = endpoint

def lambda_handler(event, context):
    # Decode the image data
    image = base64.b64decode(event['image_data'])

    # Instantiate a Predictor
    predictor = sagemaker.predictor.Predictor( endpoint, sagemaker_session=sagemaker.Session())

    # For this model the IdentitySerializer needs to be "image/png"
    #predictor.serializer = IdentitySerializer("image/png")
    print(predictor)
    # Make a prediction:
    inferences = predictor.predict(image)
    # We return the data back to the Step Function    
    event["inferences"] = inferences
    return {
        'statusCode': 200,
        "body": {"inferences":inferences}
    }


#Third funtion Filter low-confidence inferences
import json


THRESHOLD = .93


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['Payload']['body']['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    if max(inferences) >= THRESHOLD:
        meets_threshold = True
    else:
        meets_threshold = False
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }