--This SQL file is compatible with both MySQL and SQLite3
--To run SQLite3 under DOS, you must manually compile one with DJGPP, and CWSDPMI is required before running.

create table emp (
  empno numeric(4) not null,
  ename varchar(10),
  job varchar(9),
  mgr numeric(4),
  hiredate datetime,
  sal numeric(7, 2),
  comm numeric(7, 2),
  deptno numeric(2)
);

insert into emp values (7369, 'SMITH', 'CLERK', 7902, '1980-12-17', 800, null, 20);
insert into emp values (7499, 'ALLEN', 'SALESMAN', 7698, '1981-02-20', 1600, 300, 30);
insert into emp values (7521, 'WARD', 'SALESMAN', 7698, '1981-02-22', 1250, 500, 30);
insert into emp values (7566, 'JONES', 'MANAGER', 7839, '1981-04-02', 2975, null, 20);
insert into emp values (7654, 'MARTIN', 'SALESMAN', 7698, '1981-09-28', 1250, 1400, 30);
insert into emp values (7698, 'BLAKE', 'MANAGER', 7839, '1981-05-01', 2850, null, 30);
insert into emp values (7782, 'CLARK', 'MANAGER', 7839, '1981-06-09', 2450, null, 10);
insert into emp values (7788, 'SCOTT', 'ANALYST', 7566, '1982-12-09', 3000, null, 20);
insert into emp values (7839, 'KING', 'PRESIDENT', null, '1981-11-17', 5000, null, 10);
insert into emp values (7844, 'TURNER', 'SALESMAN', 7698, '1981-09-08', 1500, 0, 30);
insert into emp values (7876, 'ADAMS', 'CLERK', 7788, '1983-01-12', 1100, null, 20);
insert into emp values (7900, 'JAMES', 'CLERK', 7698, '1981-12-03', 950, null, 30);
insert into emp values (7902, 'FORD', 'ANALYST', 7566, '1981-12-03', 3000, null, 20);
insert into emp values (7934, 'MILLER', 'CLERK', 7782, '1982-01-23', 1300, null, 10);

create table dept (
  deptno numeric(2),
  dname varchar(14),
  loc varchar(13)
);

insert into dept values (10, 'ACCOUNTING', 'NEW YORK');
insert into dept values (20, 'RESEARCH', 'DALLAS');
insert into dept values (30, 'SALES', 'CHICAGO');
insert into dept values (40, 'OPERATIONS', 'BOSTON');

create table bonus (
  empno numeric(4),
  job varchar(9),
  sal numeric,
  comm numeric
);

create table salgrade (
  grade numeric,
  losal numeric,
  hisal numeric
);

insert into salgrade values (1, 700, 1200);
insert into salgrade values (2, 1201, 1400);
insert into salgrade values (3, 1401, 2000);
insert into salgrade values (4, 2001, 3000);
insert into salgrade values (5, 3001, 9999);

