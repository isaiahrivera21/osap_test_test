// deploying fast api server to pulumi  
import * as awsx from "@pulumi/awsx";
import * as k8s from "@pulumi/kubernetes";
import * as docker from "@pulumi/docker";
import * as pulumi from "@pulumi/pulumi";
// import S3ServiceAccount from "./S3ServiceAccount";
import TraefikRoute from "./TraefikRoute";

const config = new pulumi.Config(); 

// Create a repository.
const repo = new awsx.ecr.Repository("my-repo", {
    forceDelete: true,
});

// Build a Docker image from a local Dockerfile 
const image = new docker.Image("node-app", {
    build: {
        context: "../", 
    },
    imageName: pulumi.interpolate `${repo.url}:latest`,
});

// Push the image to the repository.
export const fullImageName = image.imageName;

const baseStack = new pulumi.StackReference("isaiahrivera21/osaps/osap");

// Create a k8s provider.
const provider = new k8s.Provider("provider", {
    kubeconfig: baseStack.getOutput("kubeconfig")
});


// Define labels for the Deployment
const labels = {
    app: "my-app",
};

// Create a Deployment
const appDeployment = new k8s.apps.v1.Deployment("app-deployment", {
    metadata: { labels },
    spec: {
        replicas: 1,
        selector: { matchLabels: labels },
        template: {
            metadata: { labels },
            spec: {
                containers: [{
                    name: "my-app",
                    image: image.imageName,
                    ports: [{ containerPort: 80 }],
                    env: [
                        {
                            name: "MLFLOW_TRACKING_URI",
                            value: "http://a7ff29e59272e44458bae980a656cb8f-1038010547.us-east-2.elb.amazonaws.com:5000/",
                        },
                        {
                            name: "MLFLOW_RUN_ID",
                            value: config.require("runID"),
                        },
                    ],
                }],
                serviceAccountName: baseStack.getOutput("modelsServiceAccount"), 
            },
        },
    },
}, { provider: provider });

const appService = new k8s.core.v1.Service("app-service", {
    metadata: { labels },
    spec: {
        type: "LoadBalancer", // or "ClusterIP", "NodePort", etc.
        ports: [{
            port: 80,
            targetPort: 80,
        }],
        selector: labels,
    },
}, { provider: provider });


// new TraefikRoute('my-model-route', {
//     prefix: '/models/my-model',
//     service: appService,
//     namespace: 'default',
//   }, { provider: provider })
  

// Export the image URI for potential use elsewhere
export const imageUrl = image.imageName;


// Could route this api endpoint to treafiek and might need to create a S3 service account for it 