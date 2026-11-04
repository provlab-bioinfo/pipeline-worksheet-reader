import nox

@nox.session(python=["3.11"])
def tests(session):
    session.install("pytest") # Install deps
    session.install(".")      # Install package
    session.run("pytest","-v")