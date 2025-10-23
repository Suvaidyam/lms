<template>
	<div class="text-base">
		<div
			v-if="title && (outline.data?.length || allowEdit)"
			class="grid grid-cols-[70%,30%] mb-4 px-2"
		>
			<div class="font-semibold text-lg leading-5">
				{{ __(title) }}
			</div>
			<Button size="sm" v-if="allowEdit" @click="openChapterModal()">
				{{ __('Add Chapter') }}
			</Button>
			<div v-if="props.has_semester">
				<Button size="md" v-if="allowEdit" @click="openSemesterModal()">
					{{ __('Add Semester') }}
				</Button>
			</div>
			<div v-else>
				<Button size="md" v-if="allowEdit" @click="openModuleModal()">
					{{ __('Add Module') }}
				</Button>
			</div>

			<!-- <span class="font-medium cursor-pointer" @click="expandAllChapters()">
				{{ expandAll ? __("Collapse all chapters") : __("Expand all chapters") }}
			</span> -->
		</div>
		<div
			:class="{
				'shadow rounded-md py-2 px-2': showOutline && outline.data?.length,
			}"
		>
			<Disclosure
				v-slot="{ open }"
				v-for="(chapter, index) in outline.data"
				:key="chapter.name"
				:defaultOpen="openChapterDetail(chapter.idx)"
			>
				<DisclosureButton ref="" class="flex items-center w-full p-2 group">
					<ChevronRight
						:class="{
							'rotate-90 transform duration-200': open,
							'duration-200': !open,
							hidden: chapter.is_scorm_package,
							open: index == 1,
						}"
						class="h-4 w-4 text-gray-900 stroke-1"
					/>
					<div
						class="text-base text-left font-medium leading-5 ml-2"
						@click="redirectToChapter(chapter)"
					>
						{{ chapter.title }}
					</div>
					<div class="flex ml-auto space-x-4">
						<Tooltip :text="__('Edit Chapter')" placement="bottom">
							<FilePenLine
								v-if="allowEdit"
								@click.prevent="openChapterModal(chapter)"
								class="h-4 w-4 text-gray-900 invisible group-hover:visible"
							/>
						</Tooltip>
						<Tooltip :text="__('Delete Chapter')" placement="bottom">
							<Trash2
								v-if="allowEdit"
								@click.prevent="trashChapter(chapter.name)"
								class="h-4 w-4 text-red-500 invisible group-hover:visible"
							/>
						</Tooltip>
					</div>
				</DisclosureButton>
				<DisclosurePanel v-if="!chapter.is_scorm_package">
					<Draggable
						v-if="!chapter.is_scorm_package"
						:list="chapter.lessons"
						:disabled="!allowEdit"
						item-key="name"
						group="items"
						@end="updateOutline"
						:data-chapter="chapter.name"
					>
						<template #item="{ element: lesson }">
							<div class="outline-lesson pl-8 py-2 pr-4">
								<router-link
									:to="{
										name: allowEdit ? 'LessonForm' : 'Lesson',
										params: {
											courseName: courseName,
											chapterNumber: lesson.number.split('.')[0],
											lessonNumber: lesson.number.split('.')[1],
										},
									}"
								>
									<div class="flex items-center text-sm leading-5 group">
										<MonitorPlay
											v-if="lesson.icon === 'icon-youtube'"
											class="h-4 w-4 text-gray-900 stroke-1 mr-2"
										/>
										<HelpCircle
											v-else-if="lesson.icon === 'icon-quiz'"
											class="h-4 w-4 text-gray-900 stroke-1 mr-2"
										/>
										<FileText
											v-else-if="lesson.icon === 'icon-list'"
											class="h-4 w-4 text-gray-900 stroke-1 mr-2"
										/>
										{{ lesson.title }}
										<Trash2
											v-if="allowEdit"
											@click.prevent="trashLesson(lesson.name, chapter.name)"
											class="h-4 w-4 text-red-500 ml-auto invisible group-hover:visible"
										/>
										<Check
											v-if="lesson.is_complete"
											class="h-4 w-4 text-green-700 ml-2"
										/>
									</div>
								</router-link>
							</div>
						</template>
</Draggable>
<div v-if="allowEdit" class="flex mt-2 mb-4 pl-8">
	<router-link v-if="!chapter.is_scorm_package" :to="{
							name: 'LessonForm',
							params: {
								courseName: courseName,
								chapterNumber: chapter.idx,
								lessonNumber: chapter.lessons.length + 1,
							},
						}">
		<Button>
			{{ __('Add Lesson') }}
		</Button>
	</router-link>
</div>
</DisclosurePanel>
</Disclosure>
</div> -->
		<div :class="{
			'shadow rounded-md py-2 px-2': showOutline && outline.data?.length,
		}">
			<!-- SEMESTER LEVEL -->
			<!-- SEMESTER LEVEL -->
			<Disclosure v-if="props.has_semester" v-slot="{ open }" v-for="(semester, sIndex) in outline.data" :key="semester.name"
				:defaultOpen="openSemesterDetail(semester.idx)">

				<DisclosureButton class="flex items-center w-full p-2 group">
					<ChevronRight :class="{ 'rotate-90 transform duration-200': open }" class="h-4 w-4 text-gray-900" />
					<div class="text-base font-medium ml-2">{{ semester.title }}</div>

					<div v-if="props.allowEdit" class="ml-auto  flex space-x-2 invisible group-hover:visible">
						<Tooltip :text="__('Edit Semester')" placement="bottom">
							<FilePenLine class="h-4 w-4 text-gray-800" @click.prevent="openSemesterModal(semester)" />
						</Tooltip>
						<Tooltip :text="__('Delete Semester')" placement="bottom">
							<Trash2 class="h-4 w-4 text-red-500" @click.prevent="trashSemester(semester.name)" />{{}}
						</Tooltip>
					</div>
				</DisclosureButton>

				<DisclosurePanel v-if="!semester.is_scorm_package" class="pl-4">
					<!-- MODULE LEVEL -->
					<Disclosure v-for="(module, mIndex) in semester.modules" :key="module.name"
						v-slot="{ open: modOpen }">
						<DisclosureButton class="flex items-center w-full p-2 group">
							<ChevronRight :class="{ 'rotate-90 transform duration-200': modOpen }"
								class="h-4 w-4 text-gray-800" />
							<div class="text-sm font-semibold text-gray-800 ml-2">{{ module.title }}</div>

							<div v-if="props.allowEdit" class="ml-auto flex space-x-2 invisible group-hover:visible">
								<Tooltip :text="__('Edit Module')" placement="bottom">
									<FilePenLine class="h-4 w-4 text-gray-800"
										@click.prevent="openModuleModal(module, semester)" />
								</Tooltip>
								<Tooltip :text="__('Delete Module')" placement="bottom">
									<Trash2 class="h-4 w-4 text-red-500" @click.prevent="trashModule(module.name,mIndex,semester.name)" />
								</Tooltip>
							</div>
						</DisclosureButton>

						<DisclosurePanel class="pl-4">
							<!-- TOPIC LEVEL -->
							<Disclosure v-for="(topic, tIndex) in module.topics" :key="topic.name"
								v-slot="{ open: topicOpen }">
								<DisclosureButton class="flex items-center w-full p-2 group">
									<ChevronRight :class="{ 'rotate-90 transform duration-200': topicOpen }"
										class="h-4 w-4 text-gray-700" />
									<div class="text-sm text-gray-700 ml-2">{{ topic.title }}</div>

									<div v-if="props.allowEdit"
										class="ml-auto flex space-x-2 invisible group-hover:visible">
										<Tooltip :text="__('Edit Topic')" placement="bottom">
											<FilePenLine class="h-4 w-4 text-gray-700"
												@click.prevent="openTopicModal(topic, module, semester)" />
										</Tooltip>
										<Tooltip :text="__('Delete Topic')" placement="bottom">
											<Trash2 class="h-4 w-4 text-red-500"
												@click.prevent="trashTopic(topic.name ,tIndex, module.name)" />
										</Tooltip>
									</div>
								</DisclosureButton>

								<DisclosurePanel class="pl-4">
									<!-- CHAPTER LEVEL -->
									<Disclosure v-for="(chapter, cIndex) in topic.chapters" :key="chapter.name"
										v-slot="{ open: chapterOpen }">
										<DisclosureButton class="flex items-center w-full p-2 group">
											<ChevronRight :class="{ 'rotate-90 transform duration-200': chapterOpen }"
												class="h-4 w-4 text-gray-600" />
											<div class="text-sm text-gray-600 ml-2">{{ chapter.title }}</div>

											<div v-if="props.allowEdit"
												class="ml-auto flex space-x-2 invisible group-hover:visible">
												<Tooltip :text="__('Edit Chapter')" placement="bottom">
													<FilePenLine class="h-4 w-4 text-gray-600"
														@click.prevent="openChapterModal(chapter, topic, module, semester)" />
												</Tooltip>
												<Tooltip :text="__('Delete Chapter')" placement="bottom">
													<Trash2 class="h-4 w-4 text-red-500"
														@click.prevent="trashChapter(chapter.name, cIndex, topic.name)" />
												</Tooltip>
											</div>
										</DisclosureButton>

										<!-- LESSONS -->
										<DisclosurePanel class="pl-4">
											<ul class="text-xs text-gray-500 space-y-1">
												<li v-for="lesson in chapter.lessons" :key="lesson.name"
													class="flex justify-between items-center">
													<!-- <router-link :to="{
														name: 'LessonForm1',
														params: {
															course: courseName,
															semester: semester.name,
															module: module.name,
															topic: topic.name,
															chapter: chapter.name,
															// lesson: chapter.lessons.length + 1,
															// lessonNumber: chapter.lessons.length + 1,
															lessonNumber: lesson.idx,
														}
														// params: {
														// 	courseName: courseName,
														// 	chapterNumber: chapter.idx,
														// 	lessonNumber: chapter.lessons.length + 1,
														// },
													}"> -->
													<router-link :to="{
														name: 'Lesson1',
														params: {
															course: courseName,
															semesterNumber: semester.idx,
															moduleNumber: module.idx,
															topicNumber: topic.idx,
															chapterNumber: chapter.idx,
															// lesson: chapter.lessons.length + 1,
															// lessonNumber: chapter.lessons.length + 1,
															lessonNumber: lesson.idx,
														}
														// params: {
														// 	courseName: courseName,
														// 	chapterNumber: chapter.idx,
														// 	lessonNumber: chapter.lessons.length + 1,
														// },
													}">
														<span>{{ lesson.title }}</span>
													</router-link>
													<div v-if="props.allowEdit" class="flex space-x-2">
														<!-- <Tooltip :text="__('Edit Lesson')" placement="bottom">
                        <FilePenLine class="h-4 w-4 text-gray-500" @click.prevent="openLessonModal(lesson)" />
                      </Tooltip> -->
														<Tooltip :text="__('Delete Lesson')" placement="bottom">
															<Trash2 class="h-4 w-4 text-red-500"
																@click.prevent="trashLesson(lesson.name, chapter.name)" />
														</Tooltip>
													</div>
												</li>
											</ul>

											<!-- ADD LESSON BUTTON -->
											<div v-if="allowEdit" class="mt-2">
												<router-link :to="{
													name: 'LessonForm',
													params: {
														course: courseName,
														semester: semester.name,
														module: module.name,
														topic: topic.name,
														chapter: chapter.name,
														// lesson: chapter.lessons.length + 1,
														lessonNumber: chapter.lessons.length + 1,
													}
													// params: {
													// 	courseName: courseName,
													// 	chapterNumber: chapter.idx,
													// 	lessonNumber: chapter.lessons.length + 1,
													// },
												}">
													<Button size="sm">
														{{ __('Add Lesson') }}
													</Button>
												</router-link>

											</div>
										</DisclosurePanel>
									</Disclosure>

									<!-- ADD CHAPTER BUTTON -->
									<div v-if="allowEdit" class="mt-2">
										<Button size="sm" @click="openChapterModal(null, topic, module, semester)">
											{{ __('Add Chapter') }}
										</Button>
									</div>
								</DisclosurePanel>
							</Disclosure>

							<!-- ADD TOPIC BUTTON -->
							<div v-if="allowEdit" class="mt-2">
								<Button size="sm" @click="openTopicModal(null, module, semester)">
									{{ __('Add Topic') }}
								</Button>
							</div>
						</DisclosurePanel>
					</Disclosure>

					<!-- ADD MODULE BUTTON -->
					<div v-if="allowEdit" class="mt-2">
						<Button size="sm" @click="openModuleModal(null, semester)">
							{{ __('Add Module') }}
						</Button>
					</div>
				</DisclosurePanel>
			</Disclosure>


			<Disclosure v-else v-for="(module, mIndex) in outline.data" :key="module.name" v-slot="{ open: modOpen }">
				
				<DisclosureButton class="flex items-center w-full p-2 group">
					<ChevronRight :class="{ 'rotate-90 transform duration-200': modOpen }"
						class="h-4 w-4 text-gray-800" />
					<div class="text-sm font-semibold text-gray-800 ml-2">{{ module.title }}</div>

					<div v-if="props.allowEdit" class="ml-auto flex space-x-2 invisible group-hover:visible">
						<Tooltip :text="__('Edit Module')" placement="bottom">
							<FilePenLine class="h-4 w-4 text-gray-800"
								@click.prevent="openModuleModal(module, semester)" />
						</Tooltip>
						<Tooltip :text="__('Delete Module')" placement="bottom">
							<Trash2 class="h-4 w-4 text-red-500" @click.prevent="trashModule(module.name,mIndex,props.courseName)" />
						</Tooltip>
					</div>
				</DisclosureButton>

				<DisclosurePanel class="pl-4">
					<!-- TOPIC LEVEL -->
					<Disclosure v-for="(topic, tIndex) in module.topics" :key="topic.name" v-slot="{ open: topicOpen }">
						<DisclosureButton class="flex items-center w-full p-2 group">
							<ChevronRight :class="{ 'rotate-90 transform duration-200': topicOpen }"
								class="h-4 w-4 text-gray-700" />
							<div class="text-sm text-gray-700 ml-2">{{ topic.title }}</div>

							<div v-if="props.allowEdit" class="ml-auto flex space-x-2 invisible group-hover:visible">
								<Tooltip :text="__('Edit Topic')" placement="bottom">
									<FilePenLine class="h-4 w-4 text-gray-700"
										@click.prevent="openTopicModal(topic, module, semester)" />
								</Tooltip>
								<Tooltip :text="__('Delete Topic')" placement="bottom">
									<Trash2 class="h-4 w-4 text-red-500" @click.prevent="trashTopic(topic.name,tIndex,module.name)" />
								</Tooltip>
							</div>
						</DisclosureButton>

						<DisclosurePanel class="pl-4">
							<!-- CHAPTER LEVEL -->
							<Disclosure v-for="(chapter, cIndex) in topic.chapters" :key="chapter.name"
								v-slot="{ open: chapterOpen }">
								<DisclosureButton class="flex items-center w-full p-2 group">
									<ChevronRight :class="{ 'rotate-90 transform duration-200': chapterOpen }"
										class="h-4 w-4 text-gray-600" />
									<div class="text-sm text-gray-600 ml-2">{{ chapter.title }}</div>

									<div v-if="props.allowEdit"
										class="ml-auto flex space-x-2 invisible group-hover:visible">
										<Tooltip :text="__('Edit Chapter')" placement="bottom">
											<FilePenLine class="h-4 w-4 text-gray-600"
												@click.prevent="openChapterModal(chapter, topic, module, semester)" />
										</Tooltip>
										<Tooltip :text="__('Delete Chapter')" placement="bottom">
											<Trash2 class="h-4 w-4 text-red-500"
												@click.prevent="trashChapter(chapter.name, cIndex, topic.name)" />
										</Tooltip>
									</div>
								</DisclosureButton>

								<!-- LESSONS -->
								<DisclosurePanel class="pl-4">
									<ul class="text-xs text-gray-500 space-y-1">
										<li v-for="lesson in chapter.lessons" :key="lesson.name"
											class="flex justify-between items-center">
											<!-- <router-link :to="{
														name: 'LessonForm1',
														params: {
															course: courseName,
															semester: semester.name,
															module: module.name,
															topic: topic.name,
															chapter: chapter.name,
															// lesson: chapter.lessons.length + 1,
															// lessonNumber: chapter.lessons.length + 1,
															lessonNumber: lesson.idx,
														}
														// params: {
														// 	courseName: courseName,
														// 	chapterNumber: chapter.idx,
														// 	lessonNumber: chapter.lessons.length + 1,
														// },
													}"> -->
											<router-link :to="{
												name: 'Lesson1',
												params: {
													course: courseName,
													// semesterNumber: semester.idx,
													moduleNumber: module.idx,
													topicNumber: topic.idx,
													chapterNumber: chapter.idx,
													// lesson: chapter.lessons.length + 1,
													// lessonNumber: chapter.lessons.length + 1,
													lessonNumber: lesson.idx,
												}
												// params: {
												// 	courseName: courseName,
												// 	chapterNumber: chapter.idx,
												// 	lessonNumber: chapter.lessons.length + 1,
												// },
											}">
												<span>{{ lesson.title }}</span>
											</router-link>
											<div v-if="props.allowEdit" class="flex space-x-2">
												<!-- <Tooltip :text="__('Edit Lesson')" placement="bottom">
                        <FilePenLine class="h-4 w-4 text-gray-500" @click.prevent="openLessonModal(lesson)" />
                      </Tooltip> -->
												<Tooltip :text="__('Delete Lesson')" placement="bottom">
													<Trash2 class="h-4 w-4 text-red-500"
														@click.prevent="trashLesson(lesson.name, chapter.name)" />
												</Tooltip>
											</div>
										</li>
									</ul>

									<!-- ADD LESSON BUTTON -->
									<div v-if="allowEdit" class="mt-2">
										<router-link :to="{
											name: 'LessonForm',
											params: {
												course: courseName,
												// semester: semester.name,
												module: module.name,
												topic: topic.name,
												chapter: chapter.name,
												// lesson: chapter.lessons.length + 1,
												lessonNumber: chapter.lessons.length + 1,
											}
											// params: {
											// 	courseName: courseName,
											// 	chapterNumber: chapter.idx,
											// 	lessonNumber: chapter.lessons.length + 1,
											// },
										}">
											<Button size="sm">
												{{ __('Add Lesson') }}
											</Button>
										</router-link>

									</div>
								</DisclosurePanel>
							</Disclosure>

							<!-- ADD CHAPTER BUTTON -->
							<div v-if="allowEdit" class="mt-2">
								<Button size="sm" @click="openChapterModal(null, topic, module, semester)">
									{{ __('Add Chapter') }}
								</Button>
							</div>
						</DisclosurePanel>
					</Disclosure>

					<!-- ADD TOPIC BUTTON -->
					<div v-if="allowEdit" class="mt-2">
						<Button size="sm" @click="openTopicModal(null, module, semester)">
							{{ __('Add Topic') }}
						</Button>
					</div>
				</DisclosurePanel>
			</Disclosure>

		</div>
	</div>
	<SemesterModal v-model="showSemesterModal" v-model:outline="outline" :course="courseName"
		:SemesterDetail="getCurrentSemester()" />

	<ModuleModal v-model="showModuleModal" v-model:outline="outline" :course="courseName"
		:semester="currentSemester?.name" :ModuleDetail="getCurrentModule()" :has_semester="props.has_semester" />

	<TopicModal v-model="showTopicModal" v-model:outline="outline" :course="courseName"
		:semester="currentSemester?.name" :module="currentModule?.name" :TopicDetail="getCurrentTopic()" />
	
	<ChapterModal v-model="showChapterModal" v-model:outline="outline" :course="courseName"
		:semester="currentSemester?.name" :module="currentModule?.name" :topic="currentTopic?.name"
		:chapterDetail="getCurrentChapter()" />

	<!-- 
		<ChapterModal v-model="showChapterModal" v-model:outline="outline" :course="courseName"
			:chapterDetail="getCurrentChapter()" /> -->
	<!-- <LessonModal v-model="showLessonModal" v-model:outline="outline" :course="courseName"
			:chapterDetail="getCurrentChapter()" /> -->


</template>
<script setup>
import { Button, createResource, Tooltip } from 'frappe-ui'
import { getCurrentInstance, inject, ref } from 'vue'
import Draggable from 'vuedraggable'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import {
	Check,
	ChevronRight,
	FileText,
	FilePenLine,
	HelpCircle,
	MonitorPlay,
	Trash2,
} from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import ChapterModal from '@/components/Modals/ChapterModal.vue'
import { showToast } from '@/utils'

const route = useRoute()
const router = useRouter()
const user = inject('$user')
const showChapterModal = ref(false)
const currentChapter = ref(null)
const app = getCurrentInstance()
const { $dialog } = app.appContext.config.globalProperties

const props = defineProps({
	courseName: {
		type: String,
		required: true,
	},
	showOutline: {
		type: Boolean,
		default: false,
	},
	title: {
		type: String,
		default: '',
	},
	allowEdit: {
		type: Boolean,
		default: false,
	},
	getProgress: {
		type: Boolean,
		default: false,
	},
	has_semester: {
		type: Boolean,
		default: true,
	},
})

const outline = createResource({
	url: 'lms.lms.utils.get_course_outline',
	cache: ['course_outline', props.courseName],
	params: {
		course: props.courseName,
		progress: props.getProgress,
		has_semester: props.has_semester,
	},
	auto: true,
})

const deleteLesson = createResource({
	url: 'lms.lms.api.delete_lesson',
	makeParams(values) {
		return {
			lesson: values.lesson,
			chapter: values.chapter,
		}
	},
	onSuccess() {
		outline.reload()
		showToast('Success', 'Lesson deleted successfully', 'check')
	},
})
const deleteSemester = createResource({
	url: 'lms.lms.api.delete_semester',
	makeParams(values) {
		return {
			semester: values.semester
		}
	},
	onSuccess() {
		outline.reload()
		showToast('Success', 'Semester deleted successfully', 'check')
	},
})
const removeModule = createResource({
	url: 'lms.lms.api.delete_reference',
	makeParams(values) {
		return {
			doctype: 'Course Module Child',
			idx: values.idx, // document name (ID) to delete
			parent: values.parent
		}
	},
	onSuccess() {
		outline.reload()
		showToast('Success', 'Module deleted successfully', 'check')
	},
})
// const deleteTopic = createResource({
// 	url: 'lms.lms.api.delete_topic',
// 	makeParams(values) {
// 		return {
// 			topic: values.topic
// 		}
// 	},
// 	onSuccess() {
// 		outline.reload()
// 		showToast('Success', 'Topic deleted successfully', 'check')
// 	},
// })

const removeTopic = createResource({
	url: 'lms.lms.api.delete_reference',
	makeParams(values) {
		return {
			doctype: 'Course Topic Child',
			idx: values.idx, // document name (ID) to delete
			parent: values.parent
		}
	},
	onSuccess() {
		outline.reload()
		showToast('Success', 'Topic deleted successfully', 'check')
	},
})

const updateLessonIndex = createResource({
	url: 'lms.lms.api.update_lesson_index',
	makeParams(values) {
		return {
			lesson: values.lesson,
			sourceChapter: values.sourceChapter,
			targetChapter: values.targetChapter,
			idx: values.idx,
		}
	},
	onSuccess() {
		showToast('Success', 'Lesson moved successfully', 'check')
	},
})

const trashLesson = (lessonName, chapterName) => {
	$dialog({
		title: __('Delete this lesson?'),
		message: __(
			'Deleting this lesson will permanently remove it from the course. This action cannot be undone. Are you sure you want to continue?'
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					deleteLesson.submit({
						lesson: lessonName,
						chapter: chapterName,
					})
					close()
				},
			},
		],
	})
}

const openChapterDetail = (index) => {
	return index == route.params.chapterNumber || index == 1
}

const openChapterModal = (chapter = null) => {
	currentChapter.value = chapter
	showChapterModal.value = true
}

const getCurrentChapter = () => {
	return currentChapter.value
}

const updateOutline = (e) => {
	updateLessonIndex.submit({
		lesson: e.item.__draggable_context.element.name,
		sourceChapter: e.from.dataset.chapter,
		targetChapter: e.to.dataset.chapter,
		idx: e.newIndex,
	})
}

// const deleteChapter = createResource({
// 	url: 'lms.lms.api.delete_chapter',
// 	makeParams(values) {
// 		return {
// 			chapter: values.chapter,
// 			topic:values.topic
// 		}
// 	},
// 	onSuccess() {
// 		outline.reload()
// 		showToast('Success', 'Chapter deleted successfully', 'check')
// 	},
// })
const removeChapter = createResource({
	url: 'lms.lms.api.delete_reference',
	makeParams(values) {
		return {
			doctype: 'Chapter Reference',
			idx: values.idx, // document name (ID) to delete
			parent: values.parent
		}
	},
	onSuccess() {
		outline.reload()
		showToast('Success', 'Chapter deleted successfully', 'check')
	},
})
const trashSemester = (semesterName) => {
	$dialog({
		title: __(`Delete this semester?`),
		message: __(
			'Deleting this semester will also delete all its modules, topics,chapters & lessons and permanently remove it from the course. This action cannot be undone. Are you sure you want to continue?'
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					deleteSemester.submit({ semester: semesterName })
					close()
				},
			},
		],
	})
}
const trashModule = (moduleName, mIndex,parent) => {
	$dialog({
		title: __(`Delete this module?`),
		message: __(
			'Deleting this module will also delete all its  topics,chapters & lessons and permanently remove it from the semester. This action cannot be undone. Are you sure you want to continue?'
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					removeModule.submit({ idx: mIndex, parent: parent })
					close()
				},
			},
		],
	})
}
const trashTopic = (topicName, tIndex, module=null) => {
	$dialog({
		title: __(`Delete this topic?`),
		message: __(
			'Deleting this topic will also delete all its chapters & lessons and permanently remove it from the module. This action cannot be undone. Are you sure you want to continue?'
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					// deleteTopic.submit({ topic: topicName })
					removeTopic.submit({ idx: tIndex  , parent: module})
					close()
				},
			},
		],
	})
}

const trashChapter = (chapterName, cIndex, topic=null) => {
	$dialog({
		title: __('Delete this chapter?'),
		message: __(
			'Deleting this chapter will also delete all its lessons and permanently remove it from the course. This action cannot be undone. Are you sure you want to continue?'
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					removeChapter.submit({  idx:cIndex, parent:topic })
					close()
				},
			},
		],
	})
}

const redirectToChapter = (chapter) => {
	if (!chapter.is_scorm_package) return
	event.preventDefault()
	if (props.allowEdit) return
	if (!user.data) {
		showToast(
			__('You are not enrolled'),
			__('Please enroll for this course to view this lesson'),
			'alert-circle'
		)
		return
	}

	router.push({
		name: 'SCORMChapter',
		params: {
			courseName: props.courseName,
			chapterName: chapter.name,
		},
	})
}
import { watch } from 'vue'
import m from '@editorjs/embed'

const getModuleData = createResource({
	url: 'get_module_data',  // Use your actual API path here
	auto: false,
	onSuccess(response) {
		// console.log('✅ Modules:', response)
	},
	onError(error) {
		console.error('❌ Error fetching modules:', error)
	}
})

onMounted(() => {
	// console.log("✅ onMounted triggered")
	getModuleData.submit().then(() => {
		console.log("✅ getModuleData.submit() done", getModuleData.data)
	}).catch(err => {
		console.error("❌ API Error:", err)
	})
})

// Watch for changes in the loaded data reactively
watch(() => getModuleData.data, (newData, oldData) => {
	if (newData) {
		console.log('👀 Module data changed:', newData)
	} else {
		console.log('👀 Module data is empty or reset')
	}
})


</script>
<style>
.outline-lesson:has(.router-link-active) {
	background-color: theme('colors.gray.100');
}
</style>
