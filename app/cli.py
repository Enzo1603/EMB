import os
import sys

import click
from flask_migrate import upgrade

COV = None
if os.environ.get("FLASK_COVERAGE"):
    import coverage
    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()


def register(app):
    @app.cli.command()
    @click.option("--coverage/--no-coverage", default=False, help="Run tests under code coverage.")
    @click.argument('test_names', nargs=-1)
    def test(coverage, test_names):
        """Run the unit tests."""
        if coverage and not os.environ.get('FLASK_COVERAGE'):
            import subprocess
            os.environ['FLASK_COVERAGE'] = '1'
            sys.exit(subprocess.call(sys.argv))

        import unittest
        if test_names:
            tests = unittest.TestLoader().loadTestsFromNames(test_names)
        else:
            tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)
        if COV:
            COV.stop()
            COV.save()
            print('Coverage Summary:')
            COV.report()
            basedir = os.path.abspath(os.path.dirname(__file__))
            covdir = os.path.join(basedir, 'tmp/coverage')
            COV.html_report(directory=covdir)
            print(f'HTML version: file://{covdir}/index.html')
            COV.erase()

    @app.cli.command()
    @click.option('--length', default=25,
                  help='Number of functions to include in the profiler report.')
    @click.option('--profile-dir', default=None,
                  help='Directory where profiler data files are saved.')
    def profile(length, profile_dir):
        """Start the application under the code profiler."""
        from werkzeug.middleware.profiler import ProfilerMiddleware
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                          profile_dir=profile_dir)
        app.run(debug=False)

    @app.cli.command()
    def deploy():
        """Run development tasks."""
        # migrate database to latest revision
        upgrade()

        # create or update user roles
        Role.insert_roles()
