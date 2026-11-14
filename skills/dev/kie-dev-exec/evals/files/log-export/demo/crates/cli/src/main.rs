// demo 仓库的命令行入口：读取日志文件，输出记录与按级别的统计
use std::env;
use std::fs;
use std::process::ExitCode;

fn main() -> ExitCode {
    let Some(path) = env::args().nth(1) else {
        eprintln!("用法: cli <日志文件>");
        return ExitCode::from(2);
    };
    let text = match fs::read_to_string(&path) {
        Ok(text) => text,
        Err(err) => {
            eprintln!("读取日志文件失败: {err}");
            return ExitCode::FAILURE;
        }
    };
    let entries = logfmt::parse(&text);
    print!("{}", logfmt::render(&entries));
    for (level, count) in logfmt::stats(&entries) {
        println!("统计 {level}\t{count}");
    }
    ExitCode::SUCCESS
}
