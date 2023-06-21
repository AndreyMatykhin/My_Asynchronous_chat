from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["server"],
}
setup(
    name="my_messanger_server",
    version="0.0.1",
    description="messenger_server",
    author="Andrey Matyukhin ",
    author_email="matykhinand2021@gmail.com",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('server/server.py',
                            # base='Win32GUI',
                            target_name='server.exe',
                            )]
)
