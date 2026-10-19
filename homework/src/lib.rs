//! Анализ оценок: владение строками, заимствование, enum и итераторы.
use std::collections::BTreeMap;
use std::fmt;

/// Запись владеет фамилией и вектором оценок: ссылок на входной файл нет.
#[derive(Debug, PartialEq)]
pub struct Student {
    pub name: String,
    pub grades: Vec<u8>,
}

impl Student {
    /// Неизменяемое заимствование позволяет считать среднее без копирования.
    pub fn average(&self) -> f64 {
        let sum: u32 = self.grades.iter().map(|&g| u32::from(g)).sum();
        if self.grades.is_empty() {
            0.0
        } else {
            f64::from(sum) / self.grades.len() as f64
        }
    }
}

/// Ошибка содержит номер строки и причину; panic для входных данных не нужен.
#[derive(Debug, PartialEq)]
pub enum ParseError {
    EmptyInput,
    InvalidLine { line: usize, reason: String },
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::EmptyInput => write!(f, "нет записей об оценках"),
            Self::InvalidLine { line, reason } => {
                write!(f, "строка {line}: {reason}")
            }
        }
    }
}

impl std::error::Error for ParseError {}

/// Формат: фамилия;оценка;оценка. Заголовок и кавычки не поддерживаются.
/// Пустые строки и строки комментариев, начинающиеся с #, пропускаются.
pub fn parse_students(input: &str) -> Result<Vec<Student>, ParseError> {
    let mut students = Vec::new();
    for (index, raw) in input.lines().enumerate() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let fail = |reason: &str| ParseError::InvalidLine {
            line: index + 1,
            reason: reason.to_owned(),
        };
        let mut fields = line.split(';').map(str::trim);
        let name = fields.next().unwrap_or_default();
        if name.is_empty() {
            return Err(fail("пустая фамилия"));
        }
        if students.iter().any(|s: &Student| s.name == name) {
            return Err(fail("повторная фамилия"));
        }
        let mut grades = Vec::new();
        for field in fields {
            // ? возвращает ошибку вызывающей функции, не прерывая процесс.
            let grade = field
                .parse::<u8>()
                .map_err(|_| fail("оценка должна быть целым числом 2..5"))?;
            if !(2..=5).contains(&grade) {
                return Err(fail("оценка вне диапазона 2..5"));
            }
            grades.push(grade);
        }
        if grades.is_empty() {
            return Err(fail("нет оценок"));
        }
        // Владение созданными String и Vec переносится внутрь Student.
        students.push(Student {
            name: name.to_owned(),
            grades,
        });
    }
    if students.is_empty() {
        Err(ParseError::EmptyInput)
    } else {
        Ok(students)
    }
}

/// Результат содержит ссылки: исходные записи не перемещаются и не копируются.
pub fn ranking(students: &[Student]) -> Vec<&Student> {
    let mut ranked: Vec<&Student> = students.iter().collect();
    ranked.sort_by(|a, b| {
        b.average()
            .total_cmp(&a.average())
            .then_with(|| a.name.cmp(&b.name))
    });
    ranked
}

/// BTreeMap сохраняет порядок ключей. fold накапливает частоты оценок.
pub fn histogram(students: &[Student]) -> BTreeMap<u8, usize> {
    students.iter().flat_map(|s| s.grades.iter()).fold(
        (2..=5).map(|g| (g, 0)).collect(),
        |mut counts, &g| {
            *counts.entry(g).or_default() += 1;
            counts
        },
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_unicode_and_crlf() {
        let data = parse_students("# пример\r\n Иванов ;5;4\r\n").unwrap();
        assert_eq!(data[0].name, "Иванов");
        assert_eq!(data[0].grades, vec![5, 4]);
        assert_eq!(data[0].average(), 4.5);
    }

    #[test]
    fn rejects_empty_input() {
        assert_eq!(parse_students("\n# пусто"), Err(ParseError::EmptyInput));
    }

    #[test]
    fn rejects_invalid_records() {
        for line in [";5", "Анна", "Анна;1", "Анна;6", "Анна;x", "Анна;"] {
            assert!(matches!(
                parse_students(line),
                Err(ParseError::InvalidLine { line: 1, .. })
            ));
        }
    }

    #[test]
    fn reports_duplicate_line_number() {
        assert_eq!(
            parse_students("Анна;5\nАнна;4"),
            Err(ParseError::InvalidLine {
                line: 2,
                reason: "повторная фамилия".to_owned(),
            })
        );
    }

    #[test]
    fn sorts_average_and_name_without_mutation() {
        let data = parse_students("Борис;3\nАнна;5\nВера;5").unwrap();
        let names: Vec<&str> = ranking(&data).iter().map(|s| s.name.as_str()).collect();
        assert_eq!(names, ["Анна", "Вера", "Борис"]);
        assert_eq!(data[0].name, "Борис");
    }

    #[test]
    fn counts_histogram_and_handles_empty_collections() {
        let data = parse_students("Анна;2;4;5\nБорис;4;5").unwrap();
        assert_eq!(
            histogram(&data),
            BTreeMap::from([(2, 1), (3, 0), (4, 2), (5, 2),])
        );
        assert!(ranking(&[]).is_empty());
        assert!(histogram(&[]).values().all(|&n| n == 0));
        assert_eq!(
            Student {
                name: "X".into(),
                grades: vec![]
            }
            .average(),
            0.0
        );
    }
}
