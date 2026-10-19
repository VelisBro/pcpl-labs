//! Командная оболочка отделена от функций разбора и вычислений.
use grade_analyzer::{histogram, parse_students, ranking};
use std::{env, fs, process::ExitCode};

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args == ["--help"] {
        println!("Запуск: grade_analyzer <путь к файлу>");
        println!("Формат строки: фамилия;оценка;оценка (2..5)");
        return Ok(());
    }
    if args.len() != 1 {
        return Err("нужен один путь к файлу; справка: --help".into());
    }
    let input = fs::read_to_string(&args[0])
        .map_err(|e| format!("не удалось прочитать '{}': {e}", args[0]))?;
    let students = parse_students(&input).map_err(|e| e.to_string())?;
    println!("Анализ оценок на Rust");
    println!("Записей: {}", students.len());
    println!("Рейтинг по среднему баллу:");
    for (index, student) in ranking(&students).iter().enumerate() {
        println!("{}. {}: {:.2}", index + 1, student.name, student.average());
    }
    println!("Частоты оценок:");
    for (grade, count) in histogram(&students) {
        println!("{grade}: {count}");
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(message) => {
            eprintln!("Ошибка: {message}");
            ExitCode::FAILURE
        }
    }
}
