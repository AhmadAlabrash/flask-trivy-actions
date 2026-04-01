pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID     = '612990353866'
        AWS_DEFAULT_REGION = 'eu-central-1'
        ECR_REPO          = 'python-app'
        IMAGE_TAG         = "${BUILD_NUMBER}"
        IMAGE_REPO        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}"
        IMAGE_URI         = "${IMAGE_REPO}:${IMAGE_TAG}"

        SONARQUBE_ENV     = 'sonarqube-server'
        EKS_CLUSTER_NAME  = 'attractive-rock-outfit'
        HELM_RELEASE      = 'python-app'
        K8S_NAMESPACE     = 'default'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                dir('python-app') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                dir('python-app') {
                    sh '''
                        . venv/bin/activate
                        pytest tests --maxfail=1 --disable-warnings --cov=app --cov-report=xml
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                dir('python-app') {
                    withSonarQubeEnv("${SONARQUBE_ENV}") {
                        sh '''
                            . venv/bin/activate
                            sonar-scanner
                        '''
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('python-app') {
                    sh '''
                        docker build -t ${ECR_REPO}:${IMAGE_TAG} .
                        docker tag ${ECR_REPO}:${IMAGE_TAG} ${IMAGE_URI}
                    '''
                }
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
                    docker push ${IMAGE_URI}
                '''
            }
        }

        stage('Deploy to EKS with Helm') {
            steps {
                sh '''
                    aws eks update-kubeconfig --region ${AWS_DEFAULT_REGION} --name ${EKS_CLUSTER_NAME}
                    helm upgrade --install ${HELM_RELEASE} ./helm/python-app \
                      --namespace ${K8S_NAMESPACE} \
                      --create-namespace \
                      --set image.repository=${IMAGE_REPO} \
                      --set image.tag=${IMAGE_TAG}
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}