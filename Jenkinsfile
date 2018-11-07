#!groovy

@Library('pipeline-library') _

def img

node {
    stage('build') {
        checkout(scm)
        img = buildApp(name: 'hypothesis/via')
    }

    stage('test') {
        testApp(image: img, runArgs: '-u root') {
            sh 'HTTP_PROXY= HTTPS_PROXY= pip install -q tox tox-pip-extensions'
            sh 'cd /var/lib/via && tox -e py27-tests'
        }
    }

    onlyOnMaster {
        stage('release') {
            releaseApp(image: img)
        }
    }
}

onlyOnMaster {
    milestone()
    stage('qa deploy') {
        deployApp(image: img, app: 'via', env: 'qa')
    }

    milestone()
    stage('prod deploy') {
        input(message: "Deploy to prod?")
        milestone()
        deployApp(image: img, app: 'via', env: 'prod')
    }
}
