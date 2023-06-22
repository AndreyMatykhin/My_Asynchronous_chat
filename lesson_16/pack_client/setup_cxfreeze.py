import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ['client']
}
setup(
    name="my_messanger_client",
    version="0.0.1",
    description="messenger_client",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('client/client.py',
                            # base='Win32GUI',
                            target_name='client.exe',
                            )]
)
