document.querySelectorAll('.user-management-tbl select').forEach(select => {

    function applyRoleClass() {
        select.classList.remove(
            'role-systemAdmin',
            'role-policeAdmin',
            'role-police',
            'role-user'
        );

        let role = select.value;


        if(role === 'systemAdmin'){
            select.classList.add('role-systemAdmin');
        }
        else if(role === 'policeAdmin'){
            select.classList.add('role-policeAdmin');
        }
        else if(role.includes('ps') || role.includes('mps') || role === 'police'){
            select.classList.add('role-police');
        }
        else if(role === 'user'){
            select.classList.add('role-user');
        }
    }


    applyRoleClass();


    select.addEventListener('change', applyRoleClass);
});
