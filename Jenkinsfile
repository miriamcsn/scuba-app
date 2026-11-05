// CI do scuba divelog no NKP com Jenkins.
// Cada build roda num pod efêmero: procura segredos (Gitleaks), constrói e testa
// as imagens sem Docker (kaniko), publica no Harbor e grava as novas tags no
// repositório GitOps. Flux ou Argo CD aplicam a partir de lá.
//
// Pré-requisitos no namespace do Jenkins:
//   - Secret "harbor-creds" (docker-registry) com a robot account do projeto "scuba" no Harbor
//   - Credencial Jenkins "github-pat" (usuário + token) com permissão de push no repo GitOps
pipeline {
  agent {
    kubernetes {
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: gitleaks
      image: ghcr.io/gitleaks/gitleaks:latest
      command: ["sleep"]
      args: ["9999999"]
      securityContext:
        runAsUser: 1000   # mesmo usuário do agente Jenkins, para ler e escrever no workspace
    - name: kaniko
      image: ghcr.io/osscontainertools/kaniko:debug
      command: ["sleep"]
      args: ["9999999"]
      volumeMounts:
        - name: harbor-creds
          mountPath: /kaniko/.docker
    - name: git
      image: alpine/git:latest
      command: ["sleep"]
      args: ["9999999"]
  volumes:
    - name: harbor-creds
      secret:
        secretName: harbor-creds
        items:
          - key: .dockerconfigjson
            path: config.json
'''
    }
  }

  options {
    disableConcurrentBuilds()
  }

  // Polling do GitHub a cada ~2 min: o Jenkins não precisa ficar exposto à internet.
  // Passa a valer depois do primeiro build manual (Build Now).
  triggers {
    pollSCM('H/2 * * * *')
  }

  environment {
    HARBOR      = '<HARBOR_HOST>/scuba'
    GITOPS_REPO = 'github.com/miriamcsn/scuba-gitops.git'
    // Se o certificado do Harbor for de CA interna, monte a CA no container do kaniko
    // e acrescente ao comando: --registry-certificate=<HARBOR_HOST>=/caminho/da/ca.crt
  }

  stages {
    stage('1. Segredos (Gitleaks)') {
      steps {
        container('gitleaks') {
          sh 'gitleaks dir --redact -v .'
        }
      }
    }

    stage('2. Backend: build, testes e publicação') {
      steps {
        script { env.TAG = env.GIT_COMMIT.substring(0, 7) }
        container('kaniko') {
          sh '/kaniko/executor --context=dir://$WORKSPACE/backend --dockerfile=$WORKSPACE/backend/Dockerfile --destination=$HARBOR/scuba-backend:$TAG --cleanup'
        }
      }
    }

    stage('3. Frontend: build e publicação') {
      steps {
        container('kaniko') {
          sh '/kaniko/executor --context=dir://$WORKSPACE/frontend --dockerfile=$WORKSPACE/frontend/Dockerfile --destination=$HARBOR/scuba-frontend:$TAG --cleanup'
        }
      }
    }

    stage('4. Atualizar tags no repositório GitOps') {
      steps {
        container('git') {
          withCredentials([usernamePassword(credentialsId: 'github-pat', usernameVariable: 'GH_U', passwordVariable: 'GH_T')]) {
            sh 'GITOPS_URL="https://$GH_U:$GH_T@$GITOPS_REPO" CI_NAME=jenkins-ci sh ci/update-gitops.sh "$TAG"'
          }
        }
      }
    }
  }
}
