import pytest

from six.moves.urllib.parse import quote

from ...api import MissingEntry
from .base import BaseTestFormgrade
from .manager import HubAuthNotebookServerUserManager


@pytest.mark.js
@pytest.mark.usefixtures("all_formgraders")
class TestGradebook(BaseTestFormgrade):

    def test_start(self):
        # This is just a fake test, since starting up the browser and formgrader
        # can take a little while. So if anything goes wrong there, this test
        # will fail, rather than having it fail on some other test.
        pass

    def test_login(self):
        if self.manager.jupyterhub is None:
            pytest.skip("JupyterHub is not running")

        self._get(self.manager.base_formgrade_url)
        self._wait_for_element("username_input")
        next_url = self.formgrade_url().replace(self.manager.base_url, "")
        self._check_url("{}/hub/login?next={}".format(self.manager.base_url, next_url))

        # fill out the form
        self.browser.find_element_by_id("username_input").send_keys("foobar")
        self.browser.find_element_by_id("login_submit").click()

        # check the url
        self._wait_for_gradebook_page("")

    def test_load_assignment_list(self):
        # load the main page and make sure it is the Assignments page
        self._get(self.formgrade_url())
        self._wait_for_gradebook_page("")
        self._check_breadcrumbs("Assignments")

        # load the assignments page
        self._load_gradebook_page("assignments")
        self._check_breadcrumbs("Assignments")

        # click on the "Problem Set 1" link
        self._click_link("Problem Set 1")
        self._wait_for_gradebook_page("assignments/Problem Set 1")

    def test_load_assignment_notebook_list(self):
        self._load_gradebook_page("assignments/Problem Set 1")
        self._check_breadcrumbs("Assignments", "Problem Set 1")

        # click the "Assignments" link
        self._click_link("Assignments")
        self._wait_for_gradebook_page("assignments")
        self.browser.back()

        # click on the problem link
        for problem in self.gradebook.find_assignment("Problem Set 1").notebooks:
            self._click_link(problem.name)
            self._wait_for_gradebook_page("assignments/Problem Set 1/{}".format(problem.name))
            self.browser.back()

    def test_load_assignment_notebook_submissions_list(self):
        for problem in self.gradebook.find_assignment("Problem Set 1").notebooks:
            self._load_gradebook_page("assignments/Problem Set 1/{}".format(problem.name))
            self._check_breadcrumbs("Assignments", "Problem Set 1", problem.name)

            # click the "Assignments" link
            self._click_link("Assignments")
            self._wait_for_gradebook_page("assignments")
            self.browser.back()

            # click the "Problem Set 1" link
            self._click_link("Problem Set 1")
            self._wait_for_gradebook_page("assignments/Problem Set 1")
            self.browser.back()

            submissions = problem.submissions
            submissions.sort(key=lambda x: x.id)
            for i in range(len(submissions)):
                # click on the "Submission #i" link
                self._click_link("Submission #{}".format(i + 1))
                self._wait_for_formgrader("submissions/{}/?index=0".format(submissions[i].id))
                self.browser.back()

    def test_load_student_list(self):
        # load the student view
        self._load_gradebook_page("students")
        self._check_breadcrumbs("Students")

        # click on student
        for student in self.gradebook.students:
            ## TODO: they should have a link here, even if they haven't submitted anything!
            if len(student.submissions) == 0:
                continue
            self._click_link("{}, {}".format(student.last_name, student.first_name))
            self._wait_for_gradebook_page("students/{}".format(student.id))
            self.browser.back()

    def test_load_student_assignment_list(self):
        for student in self.gradebook.students:
            self._load_gradebook_page("students/{}".format(student.id))
            self._check_breadcrumbs("Students", student.id)

            try:
                self.gradebook.find_submission("Problem Set 1", student.id)
            except MissingEntry:
                ## TODO: make sure link doesn't exist
                continue

            self._click_link("Problem Set 1")
            self._wait_for_gradebook_page("students/{}/Problem Set 1".format(student.id))

    def test_load_student_assignment_submissions_list(self):
        for student in self.gradebook.students:
            try:
                submission = self.gradebook.find_submission("Problem Set 1", student.id)
            except MissingEntry:
                ## TODO: make sure link doesn't exist
                continue

            self._load_gradebook_page("students/{}/Problem Set 1".format(student.id))
            self._check_breadcrumbs("Students", student.id, "Problem Set 1")

            for problem in self.gradebook.find_assignment("Problem Set 1").notebooks:
                submission = self.gradebook.find_submission_notebook(problem.name, "Problem Set 1", student.id)
                self._click_link(problem.name)
                self._wait_for_formgrader("submissions/{}/?index=0".format(submission.id))
                self.browser.back()
                self._wait_for_gradebook_page("students/{}/Problem Set 1".format(student.id))

    def test_switch_views(self):
        # load the main page
        self._load_gradebook_page("assignments")

        # click the "Change View" button
        self._click_link("Change View", partial=True)

        # click the "Students" option
        self._click_link("Students")
        self._wait_for_gradebook_page("students")

        # click the "Change View" button
        self._click_link("Change View", partial=True)

        # click the "Assignments" option
        self._click_link("Assignments")
        self._wait_for_gradebook_page("assignments")

    def test_formgrade_view_breadcrumbs(self):
        for problem in self.gradebook.find_assignment("Problem Set 1").notebooks:
            submissions = problem.submissions
            submissions.sort(key=lambda x: x.id)

            for i, submission in enumerate(submissions):
                self._get(self.formgrade_url("submissions/{}".format(submission.id)))
                self._wait_for_formgrader("submissions/{}/?index=0".format(submission.id))

                # click on the "Assignments" link
                self._click_link("Assignments")
                self._wait_for_gradebook_page("assignments")

                # go back
                self.browser.back()
                self._wait_for_formgrader("submissions/{}/?index=0".format(submission.id))

                # click on the "Problem Set 1" link
                self._click_link("Problem Set 1")
                self._wait_for_gradebook_page("assignments/Problem Set 1")

                # go back
                self.browser.back()
                self._wait_for_formgrader("submissions/{}/?index=0".format(submission.id))

                # click on the problem link
                self._click_link(problem.name)
                self._wait_for_gradebook_page("assignments/Problem Set 1/{}".format(problem.name))

                # go back
                self.browser.back()
                self._wait_for_formgrader("submissions/{}/?index=0".format(submission.id))

    def test_load_live_notebook(self):
        for problem in self.gradebook.find_assignment("Problem Set 1").notebooks:
            submissions = problem.submissions
            submissions.sort(key=lambda x: x.id)

            for i, submission in enumerate(submissions):
                self._get(self.formgrade_url("submissions/{}".format(submission.id)))
                self._wait_for_formgrader("submissions/{}/?index=0".format(submission.id))

                # check the live notebook link
                self._click_link("Submission #{}".format(i + 1))
                self.browser.switch_to_window(self.browser.window_handles[1])
                self._wait_for_notebook_page(self.notebook_url("autograded/{}/Problem Set 1/{}.ipynb".format(submission.student.id, problem.name)))
                self.browser.close()
                self.browser.switch_to_window(self.browser.window_handles[0])

    def test_formgrade_images(self):
        submissions = self.gradebook.find_notebook("Problem 1", "Problem Set 1").submissions
        submissions.sort(key=lambda x: x.id)

        for submission in submissions:
            self._get(self.formgrade_url("submissions/{}".format(submission.id)))
            self._wait_for_formgrader("submissions/{}/?index=0".format(submission.id))

            images = self.browser.find_elements_by_tag_name("img")
            for image in images:
                # check that the image is loaded, and that it has a width
                assert self.browser.execute_script("return arguments[0].complete", image)
                assert self.browser.execute_script("return arguments[0].naturalWidth", image) > 0

    def test_logout(self):
        """Make sure after we've logged out we can't access any of the formgrader pages."""
        if self.manager.jupyterhub is None:
            pytest.skip("JupyterHub is not running")

        # logout and wait for the login page to appear
        self._get("{}/hub".format(self.manager.base_url))
        self._wait_for_element("logout")
        self._wait_for_visibility_of_element("logout")
        element = self.browser.find_element_by_id("logout")
        element.click()
        self._wait_for_element("username_input")

        # try going to a formgrader page
        self._get(self.manager.base_formgrade_url)
        self._wait_for_element("username_input")
        next_url = self.formgrade_url().replace(self.manager.base_url, "")
        self._check_url("{}/hub/login?next={}".format(self.manager.base_url, next_url))

        # this will fail if we have a cookie for another user and try to access
        # a live notebook for that user
        if isinstance(self.manager, HubAuthNotebookServerUserManager):
            pytest.xfail("https://github.com/jupyter/jupyterhub/pull/290")

        # try going to a live notebook page
        problem = self.gradebook.find_assignment("Problem Set 1").notebooks[0]
        submission = sorted(problem.submissions, key=lambda x: x.id)[0]
        url = self.notebook_url("autograded/{}/Problem Set 1/{}.ipynb".format(submission.student.id, problem.name))
        self._get(url)
        self._wait_for_element("username_input")
        next_url = quote(url.replace(self.manager.base_url, ""))
        self._check_url("{}/hub/?next={}".format(self.manager.base_url, next_url))

