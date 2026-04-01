name: Python CI with Trivy and Docker Hub

on:
  push:
    branches: [ "main" ]

jobs:
  ci:
    runs-on: ubuntu-latest

    env:
      IMAGE_NAME: ahmad09x/python-flask-app

    steps:
      - name: Checkout source code
        uses: actions/checkout@v4

      - name: Set image tag
        run: echo "IMAGE_TAG=${GITHUB_SHA::7}" >> $GITHUB_ENV

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt

- name: Run tests
  run: |
    export PYTHONPATH=$(pwd)
    pytest tests

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: |
            ${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }}
            ${{ env.IMAGE_NAME }}:latest
          push: false

      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }}
          format: table
          exit-code: '1'
          ignore-unfixed: true
          severity: CRITICAL,HIGH

      - name: Push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }}
            ${{ env.IMAGE_NAME }}:latest

      - name: Checkout deploy repo
        uses: actions/checkout@v4
        with:
          repository: AhmadAlabrash/flask-argocd-deploy
          token: ${{ secrets.DEPLOY_REPO_TOKEN }}
          path: deploy-repo

      - name: Update Helm values with new image tag
        run: |
          sed -i "s|repository: .*|repository: ${IMAGE_NAME}|g" deploy-repo/helm/python-app/values.yaml
          sed -i "s|tag: .*|tag: \"${IMAGE_TAG}\"|g" deploy-repo/helm/python-app/values.yaml

      - name: Commit and push deploy repo changes
        run: |
          cd deploy-repo
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add .
          git commit -m "Update python app image to ${IMAGE_TAG}" || echo "No changes to commit"
          git push
