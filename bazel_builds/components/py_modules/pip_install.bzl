def _pip_install_impl(ctx):
    out = ctx.actions.declare_directory(ctx.attr.out_dir)

    interpreter = ctx.file.interpreter          # python.exe im externen Repo
    runtime = ctx.files.runtime                 # ALLE Dateien der Distribution

    args = ctx.actions.args()
    args.add("-m").add("pip").add("install")
    args.add("--requirement", ctx.file.requirements)
    args.add("--target", out.path)
    args.add("--no-compile")
    args.add("--disable-pip-version-check")
    args.add("--no-input")
    if ctx.attr.require_hashes:
        args.add("--require-hashes")

    ctx.actions.run(
        executable = interpreter,
        arguments = [args],
        inputs = depset([ctx.file.requirements] + runtime),
        outputs = [out],
        env = ctx.attr.env,
        execution_requirements = {
            "requires-network": "",
            "no-sandbox": "",
            "no-remote": "",
        },
        mnemonic = "PipInstall",
        progress_message = "pip install -> %s" % out.short_path,
    )

    return [DefaultInfo(files = depset([out]))]

pip_install_dir = rule(
    implementation = _pip_install_impl,
    attrs = {
        "requirements": attr.label(allow_single_file = True, mandatory = True),
        "interpreter": attr.label(allow_single_file = True, mandatory = True),
        "runtime": attr.label(mandatory = True),
        "out_dir": attr.string(default = "site-packages"),
        "require_hashes": attr.bool(default = True),
        "env": attr.string_dict(),
    },
)
