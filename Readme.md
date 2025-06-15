# 👗 Fashion Recommendation API - GKE Auto-Deploy with FastAPI + GPT-4

This project is a body-type-based fashion recommendation system built with **FastAPI** and integrated with **OpenAI GPT-4**. It is containerized using Docker and automatically deployed to **Google Kubernetes Engine (GKE)** via **Cloud Build Triggers** for CI/CD.

---

## 📌 Features

- 🔍 **Body Type Classification** based on user measurements.
- 🧠 **Fashion Recommendation** generated using OpenAI's GPT-4.
- 🌐 **Web UI** powered by FastAPI + Jinja2 (`index.html`).
- 🔁 **REST API** for programmatic access.
- 🚀 **CI/CD** pipeline using Cloud Build trigger on repo update.
- ☁️ **Deployed on Google Kubernetes Engine (GKE)** with external IP.

---

## 🧠 Model Logic

### 📏 Body Measurements Input
- Bust
- Waist
- Hips
- High Hip

### 🧬 Output
Classified into one of the following body types:
- `hourglass`
- `top hourglass`
- `bottom hourglass`
- `inverted triangle`
- `triangle`
- `spoon`
- `rectangle`

### 💬 GPT-4 Prompt
```
You are a fashion assistant. Recommend the best clothing style for someone with a [body_type] body type.
Suggest pieces like [fashion_items].
```

---
## ✅ 1. Define your OpenAI API Key  
Create a Kubernetes secret to securely store your OpenAI key
```
kubectl create secret generic openai-secret --from-literal=api-key=YOUR_OPENAI_KEY
```
---
## 2. Upload Kubernetes Configuration to Google Kubernetes Engine
Make sure your cluster is initialized and credentials are accessible
```
gcloud container clusters get-credentials ci-cd-cluster --zone <zone name> --project <project ID>
```
---
## 3. Cloud Build 
```
# a. Build Docker image
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/fashion-cicd-project-463004/fashion-recomm:latest', '.']
# b. Push to GCR
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/fashion-cicd-project-463004/fashion-recomm:latest']
# c. Connect to GKE
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  args:
    - '-c'
    - |
      gcloud container clusters get-credentials ci-cd-cluster --zone us-east1-c --project fashion-cicd-project-463004
#d. Apply Deployment & Service YAML
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  args:
    - '-c'
    - |
      kubectl apply -f Kubernetes/deployment.yaml
      kubectl apply -f Kubernetes/service.yaml
```
---
## 4. Push Code to GitHub Repository
Make your code changes, then push to the main branch (or the branch configured in the trigger)
```
git add .
git commit -m "Update app or model"
git push origin main
```
---
### 📦 Kubernetes Configuration
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fashion-recomm
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fashion-recomm
  template:
    metadata:
      labels:
        app: fashion-recomm
    spec:
      containers:
      - name: fashion-recomm
        image: putriarisna/fashion-recomm:latest
        ports:
        - containerPort: 80
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
```

### 🛠️ Service
```yaml
kind: Service
apiVersion: v1
metadata:
  name: fashion-recomm
spec:
  selector:
    app: fashion-recomm
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```
---
## 🌐 5. Get External IP
After the build completes, get the external IP address:
```
kubectl get service fashion-recomm
```
---

## 📊 CI/CD Pipeline Summary

```text
Git Push →
  Cloud Build Trigger →
    Docker Build →
    Image Push to GCR →
    GKE Auth →
    K8s Deployment →
    Live Recommendation API
```
---
## 🧵 Author

**Putri Dewi Arisna**  
🔗 [LinkedIn](https://www.linkedin.com/in/putri-dewi-arisna/)  