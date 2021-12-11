import os
import json

# class of student
# include students attributes


class Student():
    attrs = {
        'id': None,
        'name': None,
        'age': None
    }

    def __init__(self, **attrs):
        self.attrs = attrs

    # compare id to identify the same student
    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.attr.get('id') == other.attrs.get('id')

    # for print the object
    def __str__(self):
        return json.dumps(self.attrs, sort_keys=True, indent=4)

    # compare all not empty attributes to fuzzy match
    def fuzzy_eq(self, other):
        if not isinstance(other, self.__class__):
            return False
        # flag for not all attributes are empty
        has_val = False
        for k, v in other.attrs.items():
            # bypass empty attr
            if not v:
                continue
            else:
                has_val = True
            # different attr value
            if self.attrs.get(k) != v:
                return False
        # all passed
        # and not all empty
        if has_val:
            return True
        return False

    # check if attributes meet our requirements
    def compactable(self):
        for name in self.__class__.attrs:
            if not self.attrs.get(name):
                return False
        return True

    # update attributes from the student object
    def update(self, other):
        self.attrs = other.attrs


class MySystemException(Exception):
    pass


class MySystemExitException(MySystemException):
    pass


class MySystemStudentExistException(MySystemException):
    pass


class MySystemStudentNotExistException(MySystemException):
    pass

# class of the student information management system
# interactive with the end user, and manipulate student info in system


class SIMS():
    # clear screen for different platform
    @staticmethod
    def clear_screen():
        if os.name == 'windows':
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def raise_exit():
        raise MySystemExitException()

    def __init__(self):
        # list to store student info in system
        # won't be save to anywhere when exit the system
        self._students = []
        # the student object be manage currently
        self._selected_student = None
        # message to show for last input result
        self._cmd_msg = ''

    def draw_with_frame(self, content):
        # clear screen before draw
        self.clear_screen()
        print('{:=^60}'.format('Student Information Management System'))
        for l in content:
            print(l)
        print('{:=^60}'.format(''))
        # clear for next draw
        self._cmd_msg = ''

    def draw_with_template(self, *contents):
        self.draw_with_frame(
            [
                *contents,
                # show system statu
                '{:-^60}'.format('SYSTEM STATU'),
                f'Students Count: {len(self._students)}',
                # show the selected student
                '{:-^60}'.format('SELECTED STUDENT'),
                self._selected_student,
                # show input result
                '{:-^60}'.format('LAST INPUT RESULT'),
                '{:<60}'.format(self._cmd_msg),
            ]
        )

    # draw the main user interface
    def draw_main(self):
        self.draw_with_template(
            '{:-^60}'.format('SYSTEM HELP'),
            '\n'.join([
                '[E]xit System',
                '[V]iew Student',
                '[R]egister Student',
                '[S]earch Student',
                '[U]pdate Student',
                '[D]elete Student'
            ]),
        )

    # draw the student selection view
    def draw_select(self, student, current, total):
        self.draw_with_template(
            '{:-^60}'.format('SYSTEM HELP'),
            '\n'.join([
                '[E]xit View and Select',
                '[S]elect Student',
                '[P]review Student',
                '[N]ext Student',
            ]),
            '{:-^60}'.format(f'STUDENT({current}/{total})'),
            student
        )

    # start the system
    # delegate user input to different function
    def start(self):
        cmds = {
            'e': self.raise_exit,
            'v': self.view_select,
            'r': self.register,
            's': self.search,
            'u': self.update,
            'd': self.delete,
        }
        while True:
            try:
                self.draw_main()
                cmd = cmds.get(input('Input: ').lower())
                if cmd:
                    cmd()
                else:
                    self._cmd_msg = 'Bad Input'
            # gracefully shutdown
            except (KeyboardInterrupt, EOFError, MySystemExitException):
                if self.exit():
                    break
            except MySystemStudentNotExistException:
                self._cmd_msg = 'Student Not Exist In System'
            except MySystemStudentExistException:
                self._cmd_msg = 'Student Id Exist In System'
            finally:
                pass

    # do something gracefully shudown
    def exit(self):
        print('\nBye Bye')
        return True

    # construct student object from user input
    @classmethod
    def _get_user_input_student(self):
        return Student(**{
            k: input(f'Student {k}: '.title()) for k in Student.attrs
        })

    # accept user input then register to system
    def register(self):
        try:
            s = self._get_user_input_student()
            if not s.compactable():
                self._cmd_msg = 'Students attribute must not be empty!'
                return
            self._create(s)
            self._cmd_msg = 'Registed!'
        except KeyboardInterrupt:
            pass

    # show all students for select
    def view_select(self):
        self._view_select(self._students)

    # show students for select
    def _view_select(self, students):
        current_index = 0
        while True:
            try:
                self.draw_select(
                    students[current_index] if students else None,
                    current_index+1 if students else 0,
                    len(students)
                )
                cmd = input('Input: ').lower()
                # exit view and select loop
                if cmd == 'e':
                    break
                # select the crrent viewing student
                elif cmd == 's':
                    if students:
                        self._selected_student = students[current_index]
                        self._cmd_msg = 'Selected!'
                    else:
                        self._cmd_msg = 'No Student To Select!'
                # view previous
                elif cmd == 'p':
                    if current_index > 0:
                        current_index -= 1
                    else:
                        self._cmd_msg = "It's First Student"
                # view next
                elif cmd == 'n':
                    if current_index < len(students) - 1:
                        current_index += 1
                    else:
                        self._cmd_msg = "It's Last Student"
                else:
                    self._cmd_msg = 'Bad Input'
            # catch to exit view and select loop
            # that avoid to exit the system
            except KeyboardInterrupt:
                break

    # search student by user input
    def search(self):
        students = self._retrive(
            self._get_user_input_student(), fuzzy=True
        )
        self._view_select(students)

    def _ensure_selected_student(self):
        if not self._selected_student:
            self._cmd_msg = 'Please select a student to manage!'
            return False
        return True

    # accpt user input and use it to update the selected student
    def update(self):
        if not self._ensure_selected_student():
            return
        s = self._get_user_input_student()
        if not s.compactable():
            self._cmd_msg = 'Attributes must not be empty'
            return
        self._update(self._selected_student, s)
        self._cmd_msg = "Updated!"

    # delete selected student
    def delete(self):
        if not self._ensure_selected_student():
            return
        self._delete(self._selected_student)
        self._selected_student = None
        self._cmd_msg = 'Deleted!'

    # register new student to system
    def _create(self, student):
        # don't do register if student exist
        if self._retrive(student):
            raise MySystemStudentExistException()
        # do register, append student to list
        self._students.append(student)

    # retrive list of exist student in system by given attrs
    def _retrive(self, student, fuzzy=False):
        # match student by given attrs
        if fuzzy:
            return [s for s in self._students if s.fuzzy_eq(student)]
        # match student by given id only
        else:
            for s in self._students:
                # see Student.__eq__
                if s == student:
                    return [s]
        return []

    # update the exist student
    def _update(self, student, other):
        # don't update if the id conflict with exist student
        if self._retrive(other, True):
            raise MySystemStudentExistException()
        student.update(other)

    # delete student from system
    def _delete(self, student):
        try:
            self._students.remove(student)
        except ValueError:
            raise MySystemStudentNotExistException()


if __name__ == '__main__':
    SIMS().start()
