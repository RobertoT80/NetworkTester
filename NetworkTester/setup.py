from cx_Freeze import setup, Executable

base = "Console"

buildOptions = dict(
        compressed = False
		)

setup(
        name = "networkTester",
        version = "0.1",
        description = "A network host and webserver tester",
		options = dict(build_exe = buildOptions),
        executables = [Executable("networktester.py", base = base)])