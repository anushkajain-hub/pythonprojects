#include <stdio.h>
#include <string.h>

struct EMPLOYEE {
    char name[50];
    char designation[50];
    char gender;   
    char doj[15];
    float salary;
};

void totalEmployees(int n) {
    printf("Total Employees = %d\n", n);
}


void countGender(struct EMPLOYEE emp[], int n) {
    int male = 0, female = 0;

    for (int i = 0; i < n; i++) {
        if (emp[i].gender == 'M' || emp[i].gender == 'm')
            male++;
        else if (emp[i].gender == 'F' || emp[i].gender == 'f')
            female++;
    }

    printf("Male Employees = %d\n", male);
    printf("Female Employees = %d\n", female);
}


void highSalary(struct EMPLOYEE emp[], int n) {
    printf("\nEmployees with Salary > 10000:\n");

    for (int i = 0; i < n; i++) {
        if (emp[i].salary > 10000) {
            printf("%s (%s) - %.2f\n",
                   emp[i].name,
                   emp[i].designation,
                   emp[i].salary);
        }
    }
}


void asstManager(struct EMPLOYEE emp[], int n) {
    printf("\nEmployees with designation 'Asst Manager':\n");

    for (int i = 0; i < n; i++) {
        if (strcmp(emp[i].designation, "Asst Manager") == 0) {
            printf("%s - Salary: %.2f\n",
                   emp[i].name,
                   emp[i].salary);
        }
    }
}

int main() {
    int n;

    printf("Enter number of employees: ");
    scanf("%d", &n);

    struct EMPLOYEE emp[n];

    
    for (int i = 0; i < n; i++) {
        printf("\nEnter details of Employee %d:\n", i + 1);

        printf("Name: ");
        scanf(" %[^\n]", emp[i].name);

        printf("Designation: ");
        scanf(" %[^\n]", emp[i].designation);

        printf("Gender (M/F): ");
        scanf(" %c", &emp[i].gender);

        printf("Date of Joining: ");
        scanf(" %[^\n]", emp[i].doj);

        printf("Salary: ");
        scanf("%f", &emp[i].salary);
    }

    
    printf("\nRESULTS\n");
    totalEmployees(n);
    countGender(emp, n);
    highSalary(emp, n);
    asstManager(emp, n);

    return 0;
}