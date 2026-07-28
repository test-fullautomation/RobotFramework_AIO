"""
Starlark-Regel für Inno Setup Installer.
"""

def _inno_setup_installer_impl(ctx):
    """Implementierung der inno_setup_installer Regel."""
    
    # Output-Datei
    output = ctx.outputs.installer
    
    # Staging-Verzeichnis für alle Dateien
    staging_dir = ctx.actions.declare_directory(ctx.label.name + "_staging")
    
    # Manifest-Datei mit allen Input-Dateien
    manifest = ctx.actions.declare_file(ctx.label.name + "_manifest.txt")
    
    # Alle Input-Dateien sammeln (aus bundle)
    input_files = []
    for src in ctx.attr.bundle:
        input_files.extend(src.files.to_list())
    
    if not input_files:
        fail("Keine Input-Dateien im Bundle gefunden")
    
    # Manifest schreiben
    ctx.actions.write(
        output = manifest,
        content = "\n".join([f.path for f in input_files]),
    )
    
    # Staging-Action: Kopiere alle Dateien mit korrekten Pfaden
    ctx.actions.run(
        outputs = [staging_dir],
        inputs = input_files + [manifest],
        executable = ctx.executable._stager,
        arguments = [
            "--output-dir", staging_dir.path,
            "--manifest", manifest.path,
        ],
        mnemonic = "StagingFiles",
        progress_message = "Staging files for installer",
        execution_requirements = {
            "local": "1",
            "no-sandbox": "1",
        },
    )
    
    # Build-Arguments für ISCC
    args = ctx.actions.args()
    args.add("--iscc", ctx.attr.iscc_path)
    args.add("--iss", ctx.file.iss_template.path)
    args.add("--source-dir", staging_dir.path)
    args.add("--output", output.path)
    args.add("--version", ctx.attr.version)
    
    ctx.actions.run(
        outputs = [output],
        inputs = [staging_dir, ctx.file.iss_template],
        executable = ctx.executable._builder,
        arguments = [args],
        mnemonic = "InnoSetup",
        progress_message = "Building installer %s" % output.short_path,
        execution_requirements = {
            "local": "1",
            "no-sandbox": "1",
        },
    )
    
    return [DefaultInfo(files = depset([output]))]


inno_setup_installer = rule(
    implementation = _inno_setup_installer_impl,
    attrs = {
        "bundle": attr.label_list(
            mandatory = True,
            doc = "Die zu installierenden Dateien/Targets",
        ),
        "iss_template": attr.label(
            mandatory = True,
            allow_single_file = [".iss"],
            doc = "Inno Setup Script Template",
        ),
        "iscc_path": attr.string(
            default = "C:/workplace/Programme/InnoSetup/ISCC.exe",
            doc = "Pfad zu ISCC.exe",
        ),
        "version": attr.string(
            default = "1.0.0",
            doc = "Installer-Version",
        ),
        "installer_name": attr.string(
            default = "install_python",
            doc = "Name der Output-EXE (ohne .exe)",
        ),
        "_builder": attr.label(
            default = "//components/installer:build_installer_tool",
            executable = True,
            cfg = "exec",
        ),
        "_stager": attr.label(
            default = "//components/installer:stage_files_tool",
            executable = True,
            cfg = "exec",
        ),
    },
    outputs = {
        "installer": "%{installer_name}.exe",
    },
    doc = "Baut einen Windows Installer mit Inno Setup.",
)
