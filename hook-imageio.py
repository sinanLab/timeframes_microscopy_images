from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

# Collect all submodules
hiddenimports = collect_submodules('imageio')
hiddenimports.extend(collect_submodules('imageio_ffmpeg'))
hiddenimports.extend([
    'imageio.plugins',
    'imageio.plugins.pillow',
    'imageio.plugins.ffmpeg',
    'imageio.plugins.tifffile',
    'imageio_ffmpeg',
    'imageio_ffmpeg._utils',
    'numpy',
    'PIL',
])

# Collect data files and metadata
datas = collect_data_files('imageio')
datas.extend(collect_data_files('imageio_ffmpeg'))
datas.extend(copy_metadata('imageio'))
datas.extend(copy_metadata('imageio_ffmpeg'))
datas.extend(copy_metadata('numpy'))
datas.extend(copy_metadata('Pillow'))
