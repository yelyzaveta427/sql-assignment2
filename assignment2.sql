/*Даний запит рахує загальну кількість візитів до лікаря по певному діагнозу,
 *  фільтруючи по даті, віку пацієнта та статусу візиту, 
 * знаходить діагноз із максимальною кількістю візитів на виводить загальну ціну за візити 
 */

explain analyze

select(
	 select concat(diagnosis, ', total cost for all appointments: ', total_profit)
		from (
			select diagnosis, count(*) as count_, sum(cost) as total_profit
			from(
				select a.appointment_id,
				a.appointment_date,
				a.diagnosis,
				a.status,
				p.patient_name,
				p.patient_age,
				d.doctor_name,
				a.cost
				from appointments a
				join patients as p on a.patient_id = p.patient_id 
				join doctors as d on a.doctor_id = d.doctor_id
				where a.appointment_date >= '2024-01-01'
				and a.status = 'Completed' and p.patient_age > 15
			) as sub1
			group by diagnosis
		) as sub2
		where count_ = (
			select max(count_)
			from(
				select count(*) as count_
				from(
					select a.appointment_id,
						a.appointment_date,
						a.diagnosis,
						a.status,
						p.patient_name as patient_name,
						p.patient_age,
						d.doctor_name
					from appointments as a
					join patients as p on a.patient_id = p.patient_id
					join doctors as d on a.doctor_id = d.doctor_id
					where a.appointment_date >= '2024-01-01'
					and a.status = 'Completed' and p.patient_age > 15
				) as sub3
				group by diagnosis
			) as sub4	
		)	
) as most_popular_diagnosis;


/*Обрано індекси по даті візиту, статусу візиту та віку пацієнта, бо в запиті по цим параметрами відбувається фільтрація 
 * і вирачається час на пошук потрібних значень*/
create index idx_appointments_appointment_date on appointments(appointment_date);
create index idx_appointments_status on appointments(status);
create index idx_patients_patient_age on patients(patient_age);



--Вимикаємо використання індексів для того, щоб продемонструвати optimizer control
set enable_indexscan = off;


--Оптимізований запит із СТЕ та використанням індексів
explain analyze

with filtered_appointments as (
	select a.appointment_id,
	a.diagnosis,
	a.cost
	from appointments a
	join patients p on a.patient_id  = p.patient_id
	join doctors d on a.doctor_id  = d.doctor_id 
	where a.appointment_date  >= '2024-01-01' and a.status = 'Completed' and p.patient_age > 15
),
diagnosis_rate as (
	select diagnosis,
	count(*) as count_,
	sum(cost) as total_profit
	from filtered_appointments group by diagnosis
)
select (select concat (diagnosis, ', total cost for all appointments: ', total_profit)
from diagnosis_rate
where count_ = (select max(count_) from diagnosis_rate)
) as most_popular_diagnosis;

--відновлюємо використання індексів
reset enable_indexscan;
