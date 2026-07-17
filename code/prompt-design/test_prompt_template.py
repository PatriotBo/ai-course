import unittest

from prompt_template import PromptTemplate


class PromptTemplateTest(unittest.TestCase):
    def test_render_returns_metadata_and_messages(self) -> None:
        template = PromptTemplate(
            key="summary",
            version="v1",
            system_template="面向{audience}",
            user_template="<context>{context}</context>",
            required_variables=("audience", "context"),
        )

        rendered = template.render({"audience": "后端工程师", "context": "一次事故"})

        self.assertEqual(rendered.prompt_key, "summary")
        self.assertEqual(rendered.prompt_version, "v1")
        self.assertEqual(rendered.messages[0]["content"], "面向后端工程师")
        self.assertIn("一次事故", rendered.messages[1]["content"])

    def test_render_rejects_missing_variable(self) -> None:
        template = PromptTemplate(
            key="summary",
            version="v1",
            system_template="面向{audience}",
            user_template="{context}",
            required_variables=("audience", "context"),
        )

        with self.assertRaisesRegex(ValueError, "context"):
            template.render({"audience": "后端工程师"})

    def test_template_rejects_composite_placeholder(self) -> None:
        with self.assertRaisesRegex(ValueError, "simple identifiers"):
            PromptTemplate(
                key="bad",
                version="v1",
                system_template="你好 {user.name}",
                user_template="任务",
                required_variables=("user.name",),
            )

    def test_template_rejects_duplicate_required_variables(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicates"):
            PromptTemplate(
                key="bad",
                version="v1",
                system_template="你好 {name}",
                user_template="任务",
                required_variables=("name", "name"),
            )


if __name__ == "__main__":
    unittest.main()
