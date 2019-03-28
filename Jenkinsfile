#!groovy

@Library('pipeline-library') _

def img

node {
    stage('build') {
        checkout(scm)
        img = buildApp(name: 'hypothesis/via')
    }

    stage('test') {
        // The HTTP_PROXY and HTTPS_PROXY env vars are set in the Docker image
        // to point to squid. These need to be unset when installing test
        // dependencies as squid is not running.
        testApp(image: img, runArgs: '-u root -e HTTP_PROXY= -e HTTPS_PROXY= -e SITE_PACKAGES=true') {
            sh 'apk add py2-pip'
            sh 'pip install -q tox>=3.8.0'
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
